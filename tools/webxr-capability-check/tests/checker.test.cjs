'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { inspect, mount } = require('../checker.js');
const environment = (xr, secure = true) => ({ isSecureContext: secure, navigator: { xr } });

test('insecure context blocks queries even when XR exists', async () => {
  let calls = 0;
  const r = await inspect(environment({ isSessionSupported() { calls++; return true; } }, false));
  assert.equal(calls, 0); assert.equal(r.secure, false);
  assert.equal(r.modes['immersive-ar'].state, 'blocked');
});
test('missing navigator or XR is handled', async () => {
  for (const env of [{ isSecureContext: true }, environment(undefined)]) {
    const r = await inspect(env); assert.equal(r.xrPresent, false);
    assert.equal(r.modes['immersive-vr'].state, 'absent');
  }
});
test('XR without support method is handled', async () => {
  const r = await inspect(environment({})); assert.equal(r.xrPresent, true);
  assert.equal(r.modes['immersive-ar'].state, 'absent');
});
test('supported AR and unsupported VR are distinct and bound correctly', async () => {
  const seen = [];
  const xr = { isSessionSupported(mode) { assert.equal(this, xr); seen.push(mode); return Promise.resolve(mode === 'immersive-ar'); } };
  const r = await inspect(environment(xr));
  assert.deepEqual(seen.sort(), ['immersive-ar', 'immersive-vr']);
  assert.equal(r.modes['immersive-ar'].state, 'supported');
  assert.equal(r.modes['immersive-vr'].state, 'unsupported');
});
test('permission rejection in AR does not suppress successful VR query', async () => {
  const r = await inspect(environment({ isSessionSupported(mode) {
    return mode === 'immersive-ar' ? Promise.reject({ name: 'NotAllowedError' }) : Promise.resolve(true);
  } }));
  assert.equal(r.modes['immersive-ar'].state, 'error');
  assert.match(r.modes['immersive-ar'].text, /quyền/);
  assert.equal(r.modes['immersive-vr'].state, 'supported');
});
test('sync throw and generic rejection are caught without echoing raw input', async () => {
  for (const xr of [
    { isSessionSupported() { throw { name: 'SecurityError', message: '<private>' }; } },
    { isSessionSupported() { return Promise.reject(new Error('<private>')); } }
  ]) {
    const r = await inspect(environment(xr));
    assert.equal(r.modes['immersive-vr'].state, 'error');
    assert.doesNotMatch(r.modes['immersive-vr'].text, /private/);
  }
});
test('throwing getters for XR or method are contained', async () => {
  const nav = {}; Object.defineProperty(nav, 'xr', { get() { throw { name: 'SecurityError' }; } });
  const xr = {}; Object.defineProperty(xr, 'isSessionSupported', { get() { throw new Error('getter'); } });
  for (const env of [{ isSecureContext: true, navigator: nav }, environment(xr)]) {
    const r = await inspect(env); assert.equal(r.modes['immersive-ar'].state, 'error');
  }
});
test('non-boolean result is never treated as support', async () => {
  const r = await inspect(environment({ isSessionSupported() { return 'true'; } }));
  assert.equal(r.modes['immersive-ar'].state, 'error');
});
test('unsettled query times out independently', async () => {
  const r = await inspect(environment({ isSessionSupported(mode) { return mode === 'immersive-ar' ? new Promise(() => {}) : false; } }), 10);
  assert.equal(r.modes['immersive-ar'].state, 'timeout');
  assert.equal(r.modes['immersive-vr'].state, 'unsupported');
});
test('UI updates safely, disables during query and allows retry', async () => {
  const elements = Object.fromEntries(['check', 'progress', 'secure', 'xr', 'ar', 'vr'].map(id => [id, { textContent: '', dataset: {}, disabled: false }]));
  let click; elements.check.addEventListener = (event, callback) => { assert.equal(event, 'click'); click = callback; };
  let calls = 0;
  mount(environment({ isSessionSupported() { calls++; return Promise.resolve(false); } }), { getElementById(id) { return elements[id]; } });
  const pending = click(); assert.equal(elements.check.disabled, true); await pending;
  assert.equal(elements.check.disabled, false); assert.equal(elements.progress.dataset.complete, 'true');
  assert.match(elements.ar.textContent, /không hỗ trợ/); await click(); assert.equal(calls, 4);
});
