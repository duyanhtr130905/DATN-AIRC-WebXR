/* Capability queries only. No session, camera, storage or telemetry. */
(function (global) {
  'use strict';
  const messages = {
    supported: 'Có hỗ trợ API — chưa kiểm thử trải nghiệm thực tế.',
    unsupported: 'API báo không hỗ trợ mode này.',
    blocked: 'Chưa hỏi API: cần HTTPS hợp lệ hoặc localhost.',
    absent: 'Không có API truy vấn mode trong môi trường này.',
    timeout: 'Hết thời gian chờ; chưa xác định khả năng hỗ trợ.'
  };

  function errorMessage(error) {
    const name = error && error.name;
    if (name === 'SecurityError' || name === 'NotAllowedError') {
      return 'Bị chặn bởi quyền hoặc chính sách bảo mật; kiểm tra quyền, secure context và iframe policy.';
    }
    return 'Truy vấn API bị lỗi; chưa xác định khả năng hỗ trợ. Hãy kiểm tra runtime và thử lại.';
  }

  async function queryMode(xr, mode, timeoutMs) {
    let timer;
    try {
      const value = await Promise.race([
        Promise.resolve().then(() => xr.isSessionSupported(mode)),
        new Promise((resolve) => { timer = setTimeout(() => resolve('timeout'), timeoutMs); })
      ]);
      if (value === 'timeout') return { state: 'timeout', text: messages.timeout };
      if (typeof value !== 'boolean') return { state: 'error', text: errorMessage(null) };
      return { state: value ? 'supported' : 'unsupported', text: value ? messages.supported : messages.unsupported };
    } catch (error) {
      return { state: 'error', text: errorMessage(error) };
    } finally {
      clearTimeout(timer);
    }
  }

  async function inspect(environment, timeoutMs = 5000) {
    const secure = environment.isSecureContext === true;
    let xr;
    let accessError;
    try { xr = environment.navigator && environment.navigator.xr; } catch (error) { accessError = error; }
    const result = { secure, xrPresent: Boolean(xr), modes: {} };
    let fallback;
    if (!secure) fallback = { state: 'blocked', text: messages.blocked };
    else if (accessError) fallback = { state: 'error', text: errorMessage(accessError) };
    else if (!xr) fallback = { state: 'absent', text: messages.absent };
    else {
      try {
        if (typeof xr.isSessionSupported !== 'function') fallback = { state: 'absent', text: messages.absent };
      } catch (error) { fallback = { state: 'error', text: errorMessage(error) }; }
    }
    const modes = ['immersive-ar', 'immersive-vr'];
    await Promise.all(modes.map(async (mode) => {
      result.modes[mode] = fallback ? { ...fallback } : await queryMode(xr, mode, timeoutMs);
    }));
    return result;
  }

  function mount(environment, document) {
    const button = document.getElementById('check');
    const progress = document.getElementById('progress');
    button.addEventListener('click', async () => {
      button.disabled = true;
      progress.textContent = 'Đang kiểm tra khả năng API…';
      progress.dataset.complete = 'false';
      try {
        const result = await inspect(environment);
        document.getElementById('secure').textContent = result.secure ? 'Có — secure context.' : 'Không — hãy dùng HTTPS hợp lệ hoặc localhost.';
        document.getElementById('xr').textContent = result.xrPresent ? 'Có navigator.xr.' : 'Không có hoặc không truy cập được navigator.xr.';
        document.getElementById('ar').textContent = result.modes['immersive-ar'].text;
        document.getElementById('vr').textContent = result.modes['immersive-vr'].text;
        progress.textContent = 'Đã kiểm tra API. Thiết bị thực tế: chưa nghiệm thu AR/VR.';
      } catch (error) {
        progress.textContent = errorMessage(error);
        for (const id of ['secure', 'xr', 'ar', 'vr']) document.getElementById(id).textContent = 'Chưa xác định do lỗi kiểm tra; hãy thử lại.';
      } finally {
        button.disabled = false;
        progress.dataset.complete = 'true';
      }
    });
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { inspect, mount };
  if (global.document) mount(global, global.document);
})(typeof window !== 'undefined' ? window : globalThis);
