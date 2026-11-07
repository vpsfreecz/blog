const page = document.querySelector('[data-search-page]');
const form = page.querySelector('.search-form');
const input = form.elements.q;
const status = page.querySelector('[data-search-status]');
const list = page.querySelector('[data-search-results]');
const more = page.querySelector('[data-search-more]');
const reload = page.querySelector('[data-search-reload]');
let engine;
let matches = [];
let displayed = 0;
let generation = 0;
const batchSize = 10;

function failed() {
  list.replaceChildren();
  more.hidden = true;
  more.disabled = false;
  reload.hidden = false;
  status.textContent = page.dataset.error;
}

async function render(token) {
  const batch = await Promise.all(matches.slice(displayed, displayed + batchSize).map(result => result.data()));
  if (token !== generation) return;
  for (const result of batch) {
    const url = new URL(result.url, window.location.origin);
    if (url.origin !== window.location.origin) throw new Error('Unexpected result origin');
    const item = document.createElement('li');
    const title = document.createElement('h2');
    const link = document.createElement('a');
    link.href = url.href;
    link.textContent = result.meta.title;
    title.append(link);
    const excerpt = document.createElement('p');
    // Pagefind adds <mark> to excerpts. Parse it without inserting result HTML.
    const textOnly = result.excerpt.replace(/<[^>]*>/g, '');
    const parsed = new DOMParser().parseFromString(textOnly, 'text/html');
    excerpt.textContent = parsed.body.textContent;
    item.append(title, excerpt);
    list.append(item);
  }
  displayed += batch.length;
  more.hidden = displayed >= matches.length;
}

async function search(query) {
  const token = ++generation;
  list.replaceChildren();
  more.hidden = true;
  reload.hidden = true;
  more.disabled = false;
  displayed = 0;
  if (page.dataset.hasArticles !== 'true') {
    status.textContent = page.dataset.empty;
    return;
  }
  if (!query.trim()) {
    status.textContent = page.dataset.prompt;
    return;
  }
  status.textContent = page.dataset.loading;
  try {
    if (!engine) {
      // Pagefind 1.5.2 also cache-busts pagefind-entry.json with Date.now().
      // A fresh module URL on each page load avoids normalized-mtime ETags.
      engine = await import(`/pagefind/pagefind.js?ts=${Date.now()}`);
      await engine.options({baseUrl: '/'});
    }
    const response = await engine.search(query);
    if (token !== generation) return;
    matches = response.results;
    status.textContent = matches.length ? page.dataset.count.replace('{count}', String(matches.length)) : page.dataset.noMatches;
    await render(token);
  } catch {
    if (token === generation) failed();
  }
}

form.addEventListener('submit', event => {
  event.preventDefault();
  const url = new URL(window.location.href);
  url.searchParams.set('q', input.value);
  window.history.replaceState(null, '', url);
  search(input.value);
});
more.addEventListener('click', async () => {
  const token = generation;
  more.disabled = true;
  try { await render(token); } catch { if (token === generation) failed(); }
  finally { more.disabled = false; }
});
reload.addEventListener('click', () => window.location.reload());
input.value = new URLSearchParams(window.location.search).get('q') ?? '';
search(input.value);
