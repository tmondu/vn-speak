document.addEventListener('DOMContentLoaded', () => {
  const textInput = document.getElementById('text-input');
  const charCounter = document.getElementById('char-counter');
  const voiceSelect = document.getElementById('voice-select');
  const voiceDesc = document.getElementById('voice-desc');
  const speedSlider = document.getElementById('speed-slider');
  const speedVal = document.getElementById('speed-val');
  const silenceSlider = document.getElementById('silence-slider');
  const silenceVal = document.getElementById('silence-val');
  const generateBtn = document.getElementById('generate-btn');
  const btnText = document.getElementById('btn-text');
  const btnLoader = document.getElementById('btn-loader');
  const statusPill = document.getElementById('status-pill');
  const audioElement = document.getElementById('audio-element');
  const downloadBtn = document.getElementById('download-btn');
  const visualizer = document.getElementById('visualizer');
  
  const metricInfer = document.getElementById('metric-infer');
  const metricRate = document.getElementById('metric-rate');
  const metricQuality = document.getElementById('metric-quality');
  const metricQualitySub = document.getElementById('metric-quality-sub');
  const normPreview = document.getElementById('norm-preview');
  
  const sampleBtns = document.querySelectorAll('.sample-btn');

  const voiceMeta = {
    hoaimy: {
      desc: 'Giọng nữ phát thanh viên phòng thu 24kHz, ngắt nghỉ hơi thở tự nhiên như MC đài VTV (Đỉnh nhất 98%).',
      rate: '24.0 kHz',
      quality: '98%',
      qualitySub: 'Chuẩn Studio Vbee'
    },
    namminh: {
      desc: 'Giọng nam MC truyền cảm, âm sắc ấm và chững chạc, rất phù hợp cho tin thời sự, phóng sự và sách nói (98%).',
      rate: '24.0 kHz',
      quality: '98%',
      qualitySub: 'Chuẩn Studio MC'
    },
    chigoogle: {
      desc: 'Giọng đọc kinh điển của Google Dịch ("Chị Google"), meme quốc dân, phản hồi siêu tốc 24kHz.',
      rate: '24.0 kHz',
      quality: '85%',
      qualitySub: 'Google TTS Meme'
    },
    vieneu_aihan: {
      desc: 'VieNeu-TTS: Giọng Nữ miền Nam phong cách tin tức, phát âm rõ ràng, mượt mà truyền cảm.',
      rate: '24.0 kHz',
      quality: '95%',
      qualitySub: 'SOTA AI Miền Nam'
    },
    vieneu_adam: {
      desc: 'VieNeu-TTS: Giọng Nam miền Nam tự nhiên, ấm áp, nhịp điệu chân thực như người thật.',
      rate: '24.0 kHz',
      quality: '95%',
      qualitySub: 'SOTA AI Miền Nam'
    },
    vieneu_myduyen: {
      desc: 'VieNeu-TTS: Giọng Nữ miền Bắc phong cách đọc truyện, nhẹ nhàng, du dương.',
      rate: '24.0 kHz',
      quality: '95%',
      qualitySub: 'SOTA AI Miền Bắc'
    },
    vieneu_ductri: {
      desc: 'VieNeu-TTS: Giọng Nam miền Bắc phong cách đọc truyện, trầm ấm và cuốn hút.',
      rate: '24.0 kHz',
      quality: '95%',
      qualitySub: 'SOTA AI Miền Bắc'
    },
    vieneu_huuquan: {
      desc: 'VieNeu-TTS: Giọng Nam miền Bắc phong cách bản tin, dứt khoát, chuẩn thời sự.',
      rate: '24.0 kHz',
      quality: '95%',
      qualitySub: 'SOTA AI Miền Bắc'
    },
    nu_phothong: {
      desc: 'Mô hình Piper mới cập nhật: giọng nữ phổ thông tự nhiên hơn, chạy offline 100% trên CPU trong 150ms.',
      rate: '22.05 kHz',
      quality: '80%',
      qualitySub: 'Offline CPU Tự Nhiên'
    },
    thanh_nien: {
      desc: 'Mô hình Piper mới: giọng nam thanh niên tự tin, trẻ trung và dứt khoát, chạy offline siêu tốc.',
      rate: '22.05 kHz',
      quality: '78%',
      qualitySub: 'Offline CPU Nam Trẻ'
    },
    vais1000: {
      desc: 'Mô hình Piper VAIS-1000 nghiên cứu, âm rõ nhưng hơi đều đặn.',
      rate: '22.05 kHz',
      quality: '70%',
      qualitySub: 'Offline Tiêu Chuẩn'
    },
    '25hours': {
      desc: 'Mô hình Piper 25 Hours giọng đơn, 16kHz.',
      rate: '16.0 kHz',
      quality: '65%',
      qualitySub: 'Offline Giọng Đơn'
    },
    vivos: {
      desc: 'Mô hình Piper train từ dataset nhận dạng VIVOS: âm rè, nghẹt mũi để bạn đối chứng.',
      rate: '16.0 kHz',
      quality: '50%',
      qualitySub: 'Dataset Nhận Dạng'
    }
  };

  const sampleTexts = {
    '1': 'Theo bản tin thời sự lúc 14:30 ngày 18/09/2026 tại TP.HCM, kinh tế số và trí tuệ nhân tạo tiếp tục tăng trưởng mạnh mẽ, đóng góp hơn 25.5% vào tổng sản phẩm trên địa bàn.',
    '2': 'Dự án AI này giúp doanh nghiệp tiết kiệm 150k mỗi ngày, tương đương gần 4.5tr đồng một tháng. Toàn bộ thanh toán qua tài khoản ngân hàng diễn ra hoàn toàn tự động.',
    '3': 'Xin kính chào quý vị và các bạn. Tôi là trợ lý ảo trí tuệ nhân tạo thế hệ mới, rất vinh hạnh được đồng hành và hỗ trợ quý vị trong ngày hôm nay.',
    '4': 'Những năm tháng thanh xuân ấy trôi qua thật êm đềm như một cơn gió đầu hạ, để lại trong lòng chúng ta những ký ức ngọt ngào không thể nào phai nhạt.'
  };

  // Update char counter
  function updateCharCount() {
    charCounter.textContent = `${textInput.value.length} ký tự`;
  }
  textInput.addEventListener('input', updateCharCount);
  updateCharCount();

  // Voice description and quality change
  function updateVoiceInfo() {
    const meta = voiceMeta[voiceSelect.value] || voiceMeta.hoaimy;
    voiceDesc.textContent = meta.desc;
    metricRate.textContent = meta.rate;
    metricQuality.textContent = meta.quality;
    metricQualitySub.textContent = meta.qualitySub;
  }
  voiceSelect.addEventListener('change', updateVoiceInfo);
  updateVoiceInfo();

  // Slider controls
  speedSlider.addEventListener('input', () => {
    speedVal.textContent = `${parseFloat(speedSlider.value).toFixed(2)}x`;
  });

  silenceSlider.addEventListener('input', () => {
    silenceVal.textContent = `${parseFloat(silenceSlider.value).toFixed(2)}s`;
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
          speed: parseFloat(speedSlider.value),
          silence: parseFloat(silenceSlider.value)
        })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Lỗi xử lý server');
      }

      // Update UI with Audio
      const mime = data.mime_type || 'audio/wav';
      const audioSrc = `data:${mime};base64,${data.audio_base64}`;
      audioElement.src = audioSrc;
      audioElement.load();
      
      // Auto play
      try {
        await audioElement.play();
      } catch (err) {
        console.log('Autoplay blocked by browser policy:', err);
      }

      // Update Download Button
      const ext = mime.includes('mp3') ? 'mp3' : 'wav';
      downloadBtn.href = audioSrc;
      downloadBtn.download = `ViVoice_${voiceSelect.value}_${Date.now()}.${ext}`;
      downloadBtn.classList.remove('disabled');

      // Update Metrics
      metricInfer.textContent = `${data.infer_time_ms} ms`;
      metricRate.textContent = data.sample_rate;

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
      btnText.textContent = 'Đọc Ngay';
    }
  });
});
