/* CDP for the isolated browser started by the Python runner. Node >=22, no packages. */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const [base, debuggingPort, output] = process.argv.slice(2);
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function main() {
  const endpoint = `http://127.0.0.1:${Number(debuggingPort)}`;
  const pages = await (await fetch(endpoint + '/json', { signal: AbortSignal.timeout(5000) })).json();
  const page = pages.find(item => item.type === 'page');
  if (!page) throw new Error('Isolated browser has no page target');
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('CDP connection timeout')), 5000);
    socket.onopen = () => { clearTimeout(timer); resolve(); };
    socket.onerror = () => { clearTimeout(timer); reject(new Error('CDP connection failed')); };
  });
  let nextId = 0;
  const pending = new Map();
  socket.onmessage = event => {
    const message = JSON.parse(event.data);
    const request = pending.get(message.id);
    if (!request) return;
    clearTimeout(request.timer); pending.delete(message.id);
    message.error ? request.reject(new Error(message.error.message)) : request.resolve(message.result);
  };
  socket.onclose = () => {
    for (const request of pending.values()) { clearTimeout(request.timer); request.reject(new Error('CDP closed')); }
    pending.clear();
  };
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++nextId;
    const timer = setTimeout(() => { pending.delete(id); reject(new Error('CDP timeout: ' + method)); }, 10000);
    pending.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const evaluate = async expression => {
    const result = await send('Runtime.evaluate', { expression, returnByValue: true });
    if (result.exceptionDetails) throw new Error('Browser evaluation failed');
    return result.result.value;
  };
  const waitFor = async expression => {
    const deadline = Date.now() + 20000;
    while (Date.now() < deadline) { const value = await evaluate(expression); if (value) return value; await sleep(100); }
    throw new Error('Browser scenario deadline exceeded');
  };
  try {
    const browser = await send('Browser.getVersion');
    await send('Page.navigate', { url: base + '/tests/browser-smoke.html' });
    const report = await waitFor('window.smokeReport');
    report.browser = { product: browser.product, protocolVersion: browser.protocolVersion, mode: 'headless; GPU disabled; no performance evidence' };
    await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 900, deviceScaleFactor: 1, mobile: true });
    await send('Page.navigate', { url: base + '/index.html' });
    await waitFor('location.pathname === "/index.html" && document.readyState === "complete" && !!document.getElementById("check")');
    const actual = await evaluate('({viewport:innerWidth, scrollWidth:document.documentElement.scrollWidth, buttonWidth:document.getElementById("check").getBoundingClientRect().width})');
    const status = actual.viewport === 390 && actual.scrollWidth <= 390 ? 'PASS' : 'FAIL';
    const capture = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
    fs.writeFileSync(path.join(output, 'checker-390.png'), Buffer.from(capture.data, 'base64'));
    report.scenarios.push({ id: 'responsive-390', kind: 'viewport-emulation', status,
      expected: 'Viewport 390 CSS pixels, no horizontal overflow; screenshot contains only checker UI. Not a physical Galaxy.', actual, screenshot: 'checker-390.png' });
    if (status !== 'PASS') report.status = 'FAIL';
    process.stdout.write(JSON.stringify(report));
  } finally {
    try { await send('Browser.close'); } catch { /* Python owns process cleanup if browser already exited. */ }
    socket.close();
  }
}
main().catch(error => { process.stderr.write(error.message + '\n'); process.exitCode = 1; });
