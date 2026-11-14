'use strict';
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const scenarios = [];
async function waitFor(predicate, description) {
  const deadline = Date.now() + 12000;
  while (!predicate()) {
    if (Date.now() > deadline) throw new Error('Timeout: ' + description);
    await delay(50);
  }
}
async function run(id, kind) {
  const expected = kind === 'mocked-xr'
    ? 'Secure context; AR permission error and VR support shown independently; button re-enabled.'
    : 'Secure context; native query completes or reports absent/error/timeout; button re-enabled. No hardware support assertion.';
  try {
    const frame = document.getElementById(id);
    await waitFor(() => frame.contentDocument?.readyState === 'complete' && frame.contentDocument.getElementById('check'), 'iframe load');
    const win = frame.contentWindow;
    if (kind === 'mocked-xr') Object.defineProperty(win.navigator, 'xr', { configurable: true, value: {
      isSessionSupported(mode) { return mode === 'immersive-ar' ? Promise.reject({ name: 'NotAllowedError' }) : Promise.resolve(true); }
    } });
    const doc = frame.contentDocument;
    doc.getElementById('check').click();
    await waitFor(() => doc.getElementById('progress').dataset.complete === 'true', 'checker completion');
    const actual = Object.fromEntries(['secure', 'xr', 'ar', 'vr', 'progress'].map(key => [key, doc.getElementById(key).textContent]));
    actual.secureContext = win.isSecureContext;
    actual.buttonEnabled = !doc.getElementById('check').disabled;
    if (!actual.secureContext || !actual.buttonEnabled) throw new Error('Secure context or completion assertion failed');
    if (kind === 'mocked-xr' && (!actual.ar.includes('quyền') || !actual.vr.includes('Có hỗ trợ API'))) throw new Error('Independent rejection handling failed');
    // Also require populated terminal states; the native mode value is observational only.
    if ([actual.ar, actual.vr].some(text => !text || text === 'Chưa kiểm tra')) throw new Error('Mode result missing');
    scenarios.push({ id, kind, status: 'PASS', expected, actual });
  } catch (error) {
    scenarios.push({ id, kind, status: 'FAIL', expected, actual: { error: error.message } });
  }
}
Promise.all([run('native', 'native-browser'), run('mock', 'mocked-xr')]).then(() => {
  window.smokeReport = {
    status: scenarios.every(row => row.status === 'PASS') ? 'PASS' : 'FAIL',
    scenarios: scenarios.sort((a, b) => a.id.localeCompare(b.id)),
    hardware: { status: 'NOT RUN', reason: 'Headless desktop and mocked API do not test Galaxy, iPhone or a VR headset.' }
  };
  document.getElementById('result').textContent = JSON.stringify(window.smokeReport, null, 2);
});
