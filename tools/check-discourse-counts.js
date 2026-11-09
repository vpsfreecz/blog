// Offline execution of the real listing client; no browser, HTTP or npm dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(`${__dirname}/../assets/js/discourse-counts.js`, 'utf8');

function fixture(urls, language = 'cs-CZ') {
  const scripts = [];
  const timers = new Map();
  let timerId = 0;
  const links = urls.map((url, index) => ({
    href: `https://${index % 2 ? 'blog.vpsfree.org' : 'blog.vpsfree.cz'}/local-${index}/#comments`,
    dataset: {discourseCount: url},
    label: {textContent: '', set innerHTML(value) { assert.fail('Only textContent may render reply labels'); }},
    querySelector(selector) { assert.equal(selector, '[data-discourse-replies]'); return this.label; },
  }));
  const window = {};
  const document = {
    documentElement: {lang: language},
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
callback({counts: {[en.slice(0, -1)]: '3 odpovědí', [other.slice(0, -1)]: '0 replies',
  'https://blog.vpsfree.org/unrequested': '999 replies'}});
assert.deepEqual(run.links.map(link => link.label.textContent), [': 3 odpovědi', ': 3 odpovědi', ': 0 odpovědí']);
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
assert.equal(run.links[0].label.textContent, '');

const expectations = [
  [0, ': 0 odpovědí', ': 0 replies'],
  [1, ': 1 odpověď', ': 1 reply'],
  [2, ': 2 odpovědi', ': 2 replies'],
  [3, ': 3 odpovědi', ': 3 replies'],
  [4, ': 4 odpovědi', ': 4 replies'],
  [5, ': 5 odpovědí', ': 5 replies'],
  [11, ': 11 odpovědí', ': 11 replies'],
  [21, ': 21 odpovědí', ': 21 replies'],
  [22, ': 22 odpovědí', ': 22 replies'],
  [9007199254740990, ': 9007199254740990 odpovědí', ': 9007199254740990 replies'],
  [9007199254740991, ': 9007199254740991 odpovědí', ': 9007199254740991 replies'],
];
for (const language of ['cs-CZ', 'en']) {
  for (const native of ['en', 'cs']) {
    for (const [count, czech, english] of expectations) {
      const nativeUnit = native === 'en' ? (count === 1 ? 'reply' : 'replies') :
        (count === 1 ? 'odpověď' : 'odpovědí');
      run = fixture([en, en], language);
      run.window.vpsfreeBlogReplyCounts({counts: {[en.slice(0, -1)]: `${count} ${nativeUnit}`}});
      const expected = language === 'en' ? english : czech;
      assert.deepEqual(run.links.map(link => link.label.textContent), [expected, expected]);
    }
  }
}
for (const phrase of ['1 replies', '0 reply', '2 reply', '1 odpovědí', '0 odpověď', '2 odpověď',
  '3 odpovědi', '2 Antworten', 'no replies', ' Replies: 2', '2 replies later',
  '00 replies', '01 reply', '-1 replies', '+1 reply', '1.0 reply', '1e3 replies',
  '1,000 replies', '1 000 replies', '١ reply', '２ replies', ' 2 replies', '2 replies ',
  '2  replies', '2\treplies', '2\u00a0replies', '2 replies\n', '2 replies\r\n',
  '2 replies\u2028', '2 replies\u2029', '9007199254740992 replies', '9999999999999999 replies',
  '10000000000000000 replies', '<b>2 replies</b>', '<img src=x onerror=alert(1)>']) {
  for (const language of ['cs-CZ', 'en']) {
    run = fixture([en], language);
    run.window.vpsfreeBlogReplyCounts({counts: {[en.slice(0, -1)]: phrase}});
    assert.equal(run.links[0].label.textContent, '', `${language}: ${JSON.stringify(phrase)}`);
    assert.equal(run.scripts.length, 1);
  }
}
for (const language of ['', 'de', 'cs', 'en-US']) {
  run = fixture([en], language);
  assert.equal(run.scripts.length, 0);
  assert.equal(run.links[0].label.textContent, '');
}

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
console.log('Discourse reply client PASS: one deduplicated fixed batch, EN keys/local hrefs, known native phrases/page locales/safe integers/zero/unknown, text-only, caps/deadline/error/late callbacks');
