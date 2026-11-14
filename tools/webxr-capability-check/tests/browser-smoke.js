'use strict';
const rows = [];
async function run(frame, mock) {
  if (!frame.contentDocument.getElementById('check') || frame.contentDocument.readyState !== 'complete') await new Promise(resolve => frame.addEventListener('load', resolve, { once: true }));
  const win = frame.contentWindow;
  if (mock) Object.defineProperty(win.navigator, 'xr', { configurable: true, value: {
    isSessionSupported(mode) { return mode === 'immersive-ar' ? Promise.reject({ name: 'NotAllowedError' }) : Promise.resolve(true); }
  } });
  const doc = frame.contentDocument;
  doc.getElementById('check').click();
  for (let i = 0; i < 120 && doc.getElementById('progress').dataset.complete !== 'true'; i++) await new Promise(resolve => setTimeout(resolve, 100));
  const result = Object.fromEntries(['secure', 'xr', 'ar', 'vr', 'progress'].map(id => [id, doc.getElementById(id).textContent]));
  if (doc.getElementById('check').disabled || doc.getElementById('progress').dataset.complete !== 'true') throw new Error('UI did not finish');
  if (!win.isSecureContext) throw new Error('Expected localhost secure context');
  if (mock && (!result.ar.includes('quyền') || !result.vr.includes('Có hỗ trợ API'))) throw new Error('Independent rejection handling failed');
  rows.push({ environment: mock ? 'browser with mocked XR (not hardware)' : 'native desktop browser (not hardware AR/VR)', ...result });
}
Promise.all([run(document.getElementById('native'), false), run(document.getElementById('mock'), true)])
  .then(() => { document.getElementById('result').textContent = 'PASS\n' + JSON.stringify(rows, null, 2); })
  .catch(error => { document.getElementById('result').textContent = 'FAIL: ' + error.message; });
