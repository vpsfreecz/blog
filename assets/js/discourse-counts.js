(() => {
  const groups = new Map();
  for (const link of document.querySelectorAll('[data-discourse-count]')) {
    const exact = link.dataset.discourseCount;
    const label = link.querySelector('[data-discourse-replies]');
    if (!label) continue;
    let url;
    try { url = new URL(exact); } catch { continue; }
    if (url.origin !== 'https://blog.vpsfree.org' || url.username || url.password ||
        url.search || url.hash || !url.pathname.endsWith('/') || url.href !== exact) continue;
    const key = exact.slice(0, -1);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(label);
  }
  if (!groups.size || groups.size > 50) return;
  const endpoint = new URL('https://discourse.vpsfree.cz/embed/count');
  endpoint.searchParams.set('callback', 'vpsfreeBlogReplyCounts');
  for (const key of groups.keys()) endpoint.searchParams.append('embed_url[]', key);
  if (endpoint.href.length > 8192) return;

  const script = document.createElement('script');
  let done = false;
  const finish = () => {
    if (done) return false;
    done = true;
    clearTimeout(deadline);
    script.remove();
    // Leave a no-op for a late JSONP script; no retry or polling follows.
    window.vpsfreeBlogReplyCounts = () => {};
    return true;
  };
  window.vpsfreeBlogReplyCounts = response => {
    if (!finish()) return;
    if (!response || typeof response !== 'object' || Array.isArray(response) || !response.counts ||
        typeof response.counts !== 'object' || Array.isArray(response.counts)) return;
    for (const [key, labels] of groups) {
      if (!Object.prototype.hasOwnProperty.call(response.counts, key)) continue;
      const phrase = response.counts[key];
      if (typeof phrase !== 'string' || !phrase.trim() || phrase.length > 256) continue;
      for (const label of labels) label.textContent = `: ${phrase}`;
    }
  };
  const deadline = setTimeout(finish, 5000);
  script.async = true;
  script.onerror = finish;
  script.src = endpoint.href;
  document.head.append(script);
})();
