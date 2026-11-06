# vpsFree.cz blog

Hugo builds Czech and English sites for `blog.vpsfree.cz` and
`blog.vpsfree.org`. Each site uses its own host root. This scaffold contains
synthetic draft fixtures; it has no imported articles or production discussion
integration.

```sh
nix develop -c bin/check
nix build .#site
nix develop -c bin/preview
```

The preview shows repository content, including drafts, on loopback: Czech at
<http://localhost:1313/>, English at <http://localhost:1314/>. Its language switches
link paired local pages. Add `--fixtures` to preview only the isolated synthetic
demo instead. The normal production build never reads `fixtures/` and excludes
drafts. Preview pages contain no Discourse scripts or iframes. Agent-owned previews
in the managed workspace use its registered temporary-service command.

`nix develop -c bin/preview --vpn --fixtures` serves the synthetic demo on the
VPN address `172.16.106.40:4567`: Czech at
<http://aitherdev.int.vpsfree.cz:4567/> and English at
<http://aitherdev.int.vpsfree.cz:4567/en/>. English fixture articles keep their
explicit root paths, such as `/synthetic-example_1/`; only the English homepage
and feed use `/en/`. This single-origin preview is separate from production's
two host roots. `--vpn` without `--fixtures` shows real repository drafts on
that VPN listener. Only share drafts intended for everyone with VPN access.
`bin/preview --help` lists these options; both flags can be combined in either
order. No proxy or firewall changes are part of the preview command.

`result/cs/` and `result/en/` are separate document roots. Both include `/feed/`
and a sitemap. `result/metadata.json` records source/build inputs and SHA-256
hashes outside those served roots. The locked Nixpkgs input fixes Hugo and Python
versions. CSS has a content hash in its filename.

With the preview running, `nix develop -c bin/check --preview` also checks both
local `/feed/` endpoints. Hugo's preview configuration rewrites that URL to
`/feed/index.xml` internally and sets its RSS content type. Production hosting
must provide the same internal mapping and `application/rss+xml` response;
generic directory indexing is insufficient.

## Content contract

Articles use `content/posts/<article_id>/index.cs.md` and `index.en.md`. Each
variant declares `title`, original `date`, `lastmod`, `draft`, an explicit
root-relative `url`, and matching `translationKey` and `params.article_id`.
Imported IDs use `wp-<post_id>`; new IDs must use another namespace. Keep a
published URL and article ID stable. A missing translation remains absent.

`data/articles.json` maps article IDs to shared `discussion_url`, `author_ids`
and optional `legacy_post_id`. `discussion_url` is the original absolute Czech
permalink, independent of each translation's canonical URL. `data/authors.json`
maps stable author IDs to public `name` and optional approved public fields.
Optional historical comments will live in
`data/legacy-comments/<article_id>.json`; their importer/rendering contract is
not implemented here. Missing shared data is tolerated by the shell.

The RSS shell has no items yet. Legacy feed GUIDs, full-content serialization,
imported HTML, historic comments, real authoring/translation workflows, CI and
deployment belong to later packages. Do not use this scaffold for a production
cutover. Keep raw exports, email addresses, credentials and private operator
data outside this repository and its build inputs.
