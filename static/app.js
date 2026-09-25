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
  const metricRate = document.getElementById('metric-rate');
  const metricQuality = document.getElementById('metric-quality');
  const normPreview = document.getElementById('norm-preview');
  
  const sampleBtns = document.querySelectorAll('.sample-btn');

  const apiKeyContainer = document.getElementById('api-key-container');
  const elevenApiKeyInput = document.getElementById('eleven-api-key');
  const toggleKeyBtn = document.getElementById('toggle-key-btn');

  // Load saved API key from localStorage if available
  const savedApiKey = localStorage.getItem('elevenlabs_api_key');
  if (savedApiKey && elevenApiKeyInput) {
    elevenApiKeyInput.value = savedApiKey;
  }

  // Voice descriptions and metadata
  const voiceMeta = {
    adam_kokoro: {
      desc: 'Giọng Adam từ mô hình AI mã nguồn mở Kokoro-82M: chạy trực tiếp offline trên máy, hoàn toàn miễn phí 100% không cần key!',
      rate: '24.0 kHz',
      quality: 'AI Offline (Free)',
      requiresKey: false
    },
    andrew: {
      desc: 'Giọng nam đàm thoại phong cách Mỹ, hỗ trợ đa ngôn ngữ, phong thái tự tin và chân thực (Edge-TTS Miễn phí).',
      rate: '24.0 kHz',
      quality: '97% Tự nhiên',
      requiresKey: false
    },
    brian: {
      desc: 'Giọng nam đàm thoại ấm áp, gần gũi, đa ngôn ngữ linh hoạt (Edge-TTS Miễn phí).',
      rate: '24.0 kHz',
      quality: '97% Tự nhiên',
      requiresKey: false
    },
    namminh: {
      desc: 'Giọng nam MC truyền cảm, âm sắc ấm và chững chạc, rất phù hợp cho tin thời sự và sách nói (Edge-TTS Miễn phí).',
      rate: '24.0 kHz',
      quality: '98% Studio Vbee',
      requiresKey: false
    },
    hoaimy: {
      desc: 'Giọng nữ phát thanh viên miền Bắc, truyền cảm, ngắt nghỉ hơi thở chân thực (Edge-TTS Miễn phí).',
      rate: '24.0 kHz',
      quality: '98% Studio Vbee',
      requiresKey: false
    },
    adam_eleven: {
      desc: 'Giọng nam huyền thoại ElevenLabs: siêu thực, trầm ấm, truyền cảm sâu sắc (Đọc tiếng Việt & Anh đỉnh cao, cần API Key).',
      rate: '44.1 kHz',
      quality: 'Siêu thực',
      requiresKey: true
    },
    chigoogle: {
      desc: 'Giọng đọc Google Dịch ("Chị Google") quen thuộc, chuẩn meme quốc dân, phản hồi siêu tốc.',
      rate: '24.0 kHz',
      quality: 'Kinh điển',
      requiresKey: false
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

  // Voice selector change handler
  function onVoiceChange() {
    const key = voiceSelect.value;
    const meta = voiceMeta[key] || voiceMeta.hoaimy;
    voiceDesc.textContent = meta.desc;
    if (metricRate) metricRate.textContent = meta.rate;
    if (metricQuality) metricQuality.textContent = meta.quality;

    if (meta.requiresKey) {
      apiKeyContainer.classList.remove('hidden');
    } else {
      apiKeyContainer.classList.add('hidden');
    }
  }
  voiceSelect.addEventListener('change', onVoiceChange);
  onVoiceChange();

  // Save API key on change
  if (elevenApiKeyInput) {
    elevenApiKeyInput.addEventListener('input', () => {
      localStorage.setItem('elevenlabs_api_key', elevenApiKeyInput.value.trim());
    });
  }

  // Toggle API key visibility
  if (toggleKeyBtn && elevenApiKeyInput) {
    toggleKeyBtn.addEventListener('click', () => {
      const isPass = elevenApiKeyInput.type === 'password';
      elevenApiKeyInput.type = isPass ? 'text' : 'password';
    });
  }

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

    const selectedVoiceKey = voiceSelect.value;
    const isEleven = selectedVoiceKey === 'adam_eleven';
    const apiKey = elevenApiKeyInput ? elevenApiKeyInput.value.trim() : '';

    if (isEleven && !apiKey) {
      apiKeyContainer.classList.remove('hidden');
      elevenApiKeyInput.focus();
      alert('Vui lòng nhập ElevenLabs API Key để sử dụng giọng Adam! (Đăng ký miễn phí tại elevenlabs.io)');
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
          voice: selectedVoiceKey,
          speed: parseFloat(speedSlider.value),
          api_key: apiKey
        })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Lỗi xử lý server');
      }

      // Update UI with Audio
      const mime = data.mime_type || 'audio/mp3';
      const audioSrc = `data:${mime};base64,${data.audio_base64}`;
      audioElement.src = audioSrc;
      audioElement.load();
      
      // Auto play
      try {
        await audioElement.play();
      } catch (err) {
        console.log('Autoplay policy prevented auto-playback:', err);
      }

      // Update Download Button
      const ext = mime.includes('wav') ? 'wav' : 'mp3';
      downloadBtn.href = audioSrc;
      downloadBtn.download = `ViVoice_${voiceSelect.value}_${Date.now()}.${ext}`;
      downloadBtn.classList.remove('disabled');

      // Update Metrics
      metricInfer.textContent = `${data.infer_time_ms} ms`;
      if (data.sample_rate) metricRate.textContent = data.sample_rate;

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
