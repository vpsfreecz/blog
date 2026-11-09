// Offline execution of the real listing client; no browser, HTTP or npm dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/../assets/js/discourse-counts.js`, 'utf8');

function fixture(urls) {
  const scripts = [];
  const timers = new Map();
  let timerId = 0;
  const links = urls.map((url, index) => ({
    href: `https://${index % 2 ? 'blog.vpsfree.org' : 'blog.vpsfree.cz'}/local-${index}/#comments`,
    dataset: {discourseCount: url},
    label: {textContent: ''},
    querySelector(selector) { assert.equal(selector, '[data-discourse-replies]'); return this.label; },
  }));
  const window = {};
  const document = {
    querySelectorAll(selector) { assert.equal(selector, '[data-discourse-count]'); return links; },
    createElement(tag) { assert.equal(tag, 'script'); return {remove() { this.removed = true; }}; },
    head: {append(script) { scripts.push(script); }},
  };
  const context = {window, document, URL, Map, setTimeout(callback, milliseconds) {
    assert.equal(milliseconds, 5000); timers.set(++timerId, callback); return timerId;
  }, clearTimeout(id) { timers.delete(id); }};
  vm.runInNewContext(source, context);
  return {links, scripts, timers, window};
}

const en = 'https://blog.vpsfree.org/an_english/article/';
const other = 'https://blog.vpsfree.org/other/';
let run = fixture([en, en, other]);
assert.equal(run.scripts.length, 1);
assert.equal(run.scripts[0].async, true);
const request = new URL(run.scripts[0].src);
assert.equal(request.origin + request.pathname, 'https://discourse.vpsfree.cz/embed/count');
assert.equal(request.searchParams.get('callback'), 'vpsfreeBlogReplyCounts');
assert.deepEqual(request.searchParams.getAll('embed_url[]'), [en.slice(0, -1), other.slice(0, -1)]);
assert.equal(request.searchParams.has('tl'), false);
const beforeHrefs = run.links.map(link => link.href);
const callback = run.window.vpsfreeBlogReplyCounts;
callback({counts: {[en.slice(0, -1)]: '3 odpovědi', [other.slice(0, -1)]: '0 replies',
  'https://blog.vpsfree.org/unrequested': '999 replies'}});
assert.deepEqual(run.links.map(link => link.label.textContent), [': 3 odpovědi', ': 3 odpovědi', ': 0 replies']);
assert.deepEqual(run.links.map(link => link.href), beforeHrefs);
assert.equal(run.timers.size, 0);
callback({counts: {[en.slice(0, -1)]: 'late'}});
run.window.vpsfreeBlogReplyCounts({counts: {[en.slice(0, -1)]: 'duplicate'}});
assert.equal(run.links[0].label.textContent, ': 3 odpovědi');

for (const reply of [null, {}, {counts: null}, {counts: []}, {counts: 42},
  {counts: {[en]: 'wrong unnormalized key'}},
  {counts: {[en.slice(0, -1) + '#discourse-comments']: 'wrong anchor key'}},
  {counts: {[en.slice(0, -1)]: 0}}, {counts: {[en.slice(0, -1)]: ''}},
  {counts: {[en.slice(0, -1)]: 'x'.repeat(257)}},
  {counts: Object.create({[en.slice(0, -1)]: 'inherited'})}]) {
  run = fixture([en]);
  run.window.vpsfreeBlogReplyCounts(reply);
  assert.equal(run.links[0].label.textContent, '');
  assert.equal(run.scripts.length, 1);
}
run = fixture([en]);
run.window.vpsfreeBlogReplyCounts({counts: {[en.slice(0, -1)]: '<img src=x onerror=alert(1)>'}});
assert.equal(run.links[0].label.textContent, ': <img src=x onerror=alert(1)>');
for (const fail of ['timeout', 'error']) {
  run = fixture([en]);
  const late = run.window.vpsfreeBlogReplyCounts;
  if (fail === 'timeout') [...run.timers.values()][0]();
  else run.scripts[0].onerror();
  late({counts: {[en.slice(0, -1)]: 'late reply'}});
  run.window.vpsfreeBlogReplyCounts({counts: {[en.slice(0, -1)]: 'late reply'}});
  assert.equal(run.links[0].label.textContent, '');
  assert.equal(run.scripts.length, 1);
  assert.equal(run.scripts[0].removed, true);
}
for (const urls of [[], ['https://untrusted.invalid/article/'], ['http://blog.vpsfree.org/article/'],
  ['https://user@blog.vpsfree.org/article/'], ['https://blog.vpsfree.org/article/?x=1'],
  Array.from({length: 51}, (_, index) => `https://blog.vpsfree.org/article-${index}/`),
  [`https://blog.vpsfree.org/${'long'.repeat(2200)}/`]]) {
  run = fixture(urls);
  assert.equal(run.scripts.length, 0);
  assert.equal(run.timers.size, 0);
}
console.log('Discourse reply client PASS: one deduplicated fixed batch, EN keys/local hrefs, phrases/zero/unknown, text-only, caps/deadline/error/late callbacks');
