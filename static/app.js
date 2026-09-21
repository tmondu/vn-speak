document.addEventListener('DOMContentLoaded', () => {
  const textInput = document.getElementById('text-input');
  const charCounter = document.getElementById('char-counter');
  const voiceSelect = document.getElementById('voice-select');
  const voiceDesc = document.getElementById('voice-desc');
  const speedSlider = document.getElementById('speed-slider');
  const speedVal = document.getElementById('speed-val');
  const generateBtn = document.getElementById('generate-btn');
  const btnText = document.getElementById('btn-text');
  const btnLoader = document.getElementById('btn-loader');
  const statusPill = document.getElementById('status-pill');
  const audioElement = document.getElementById('audio-element');
  const downloadBtn = document.getElementById('download-btn');
  const visualizer = document.getElementById('visualizer');
  
  const metricInfer = document.getElementById('metric-infer');
  const normPreview = document.getElementById('norm-preview');
  
  const sampleBtns = document.querySelectorAll('.sample-btn');

  const voiceMeta = {
    hoaimy: {
      desc: 'Giọng nữ phát thanh viên miền Bắc, truyền cảm, ngắt nghỉ hơi thở chân thực (Chuẩn Studio Vbee 98%).'
    },
    namminh: {
      desc: 'Giọng nam MC truyền cảm, âm sắc ấm và chững chạc, rất phù hợp cho tin thời sự và sách nói (Chuẩn Studio 98%).'
    },
    chigoogle: {
      desc: 'Giọng đọc Google Dịch ("Chị Google") quen thuộc, chuẩn meme quốc dân, phản hồi siêu tốc.'
    }
  };

  const sampleTexts = {
    '1': 'Theo bản tin thời sự lúc 14:30 ngày 18/09/2026 tại TP.HCM, kinh tế số và trí tuệ nhân tạo tiếp tục tăng trưởng mạnh mẽ, đóng góp hơn 25.5% vào tổng sản phẩm trên địa bàn.',
    '2': 'Dự án AI này giúp doanh nghiệp tiết kiệm 150k mỗi ngày, tương đương gần 4.5tr đồng một tháng. Mọi quy trình thanh toán ngân hàng đều được tự động hóa.',
    '3': 'Xin kính chào quý vị và các bạn. Tôi là trợ lý ảo trí tuệ nhân tạo thế hệ mới, rất vinh hạnh được đồng hành và hỗ trợ quý vị trong ngày hôm nay.',
    '4': 'Những năm tháng thanh xuân ấy trôi qua thật êm đềm như một cơn gió đầu hạ, để lại trong lòng chúng ta những ký ức ngọt ngào không thể nào phai nhạt.'
  };

  // Update char counter
  function updateCharCount() {
    charCounter.textContent = `${textInput.value.length} ký tự`;
  }
  textInput.addEventListener('input', updateCharCount);
  updateCharCount();

  // Voice description change
  voiceSelect.addEventListener('change', () => {
    const meta = voiceMeta[voiceSelect.value] || voiceMeta.hoaimy;
    voiceDesc.textContent = meta.desc;
  });

  // Slider control
  speedSlider.addEventListener('input', () => {
    speedVal.textContent = `${parseFloat(speedSlider.value).toFixed(2)}x`;
  });

  // Sample buttons
  sampleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-sample');
      if (sampleTexts[id]) {
        textInput.value = sampleTexts[id];
        updateCharCount();
        textInput.focus();
      }
    });
  });

  // Audio play/pause visualizer sync
  audioElement.addEventListener('play', () => {
    visualizer.classList.add('playing');
  });
  audioElement.addEventListener('pause', () => {
    visualizer.classList.remove('playing');
  });
  audioElement.addEventListener('ended', () => {
    visualizer.classList.remove('playing');
  });

  // Generate TTS
  generateBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    if (!text) {
      alert('Vui lòng nhập văn bản cần đọc!');
      return;
    }

    // Set loading state
    generateBtn.disabled = true;
    btnLoader.classList.remove('hidden');
    btnText.textContent = 'Đang tạo giọng đọc...';
    statusPill.textContent = 'Đang xử lý';
    statusPill.className = 'status-pill status-busy';

    try {
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: text,
          voice: voiceSelect.value,
          speed: parseFloat(speedSlider.value)
        })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Lỗi xử lý server');
      }

      // Update UI with Audio
      const audioSrc = `data:audio/mp3;base64,${data.audio_base64}`;
      audioElement.src = audioSrc;
      audioElement.load();
      
      // Auto play
      try {
        await audioElement.play();
      } catch (err) {
        console.log('Autoplay policy prevented auto-playback:', err);
      }

      // Update Download Button
      downloadBtn.href = audioSrc;
      downloadBtn.download = `ViVoice_${voiceSelect.value}_${Date.now()}.mp3`;
      downloadBtn.classList.remove('disabled');

      // Update Metrics
      metricInfer.textContent = `${data.infer_time_ms} ms`;

      // Update Normalized Preview
      normPreview.textContent = data.normalized_text;

      statusPill.textContent = 'Thành công';
      statusPill.className = 'status-pill status-ready';

    } catch (error) {
      console.error(error);
      alert('Lỗi tạo giọng nói: ' + error.message);
      statusPill.textContent = 'Lỗi';
      statusPill.className = 'status-pill status-busy';
    } finally {
      generateBtn.disabled = false;
      btnLoader.classList.add('hidden');
      btnText.textContent = 'Đọc Ngay (Chất lượng Studio)';
    }
  });
});
