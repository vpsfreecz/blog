# vpsFree.cz blog

Hugo builds Czech and English sites for `blog.vpsfree.cz` and
`blog.vpsfree.org`. Each site uses its own host root. The repository contains
125 imported Czech articles, their public bylines, historical comments and
media. English translations remain drafts until human review. Production
Discourse integration and automatic deployment are not implemented.

For a new article or translation, follow [the author guide](docs/authoring.md).
Agents start with [AGENTS.md](AGENTS.md) and can read the repository's
[authoring skill](skills/blog-authoring/SKILL.md) without installing anything.

```sh
nix develop -c bin/check
nix build .#site
nix develop -c bin/preview
```

The preview shows repository content, including drafts, on loopback: Czech at
<http://localhost:1313/>, English at <http://localhost:1314/>. Its language switches
link paired local pages. Add `--fixtures` to preview only the isolated synthetic
demo instead. The normal production build never reads `fixtures/` and excludes
drafts. Preview pages retain approved historical media iframes and contain no
production Discourse scripts or comment embeds. Agent-owned previews
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

New articles use `content/posts/<article_id>/index.cs.md` and `index.en.md`.
Imported articles use native `index.cs.html` and `index.en.html` bundles. Each
variant declares `title`, original `date`, `lastmod`, `draft`, an explicit
root-relative `url`, and matching `translationKey` and `params.article_id`.
Imported IDs use `wp-<post_id>`; new IDs must use another namespace. Keep a
published URL and article ID stable. A missing translation remains absent.

`data/articles.json` maps article IDs to shared `discussion_url`, `author_ids`,
per-language `feed_guids` and optional `legacy_post_id`. `discussion_url` is the
original absolute Czech
permalink, independent of each translation's canonical URL. `data/authors.json`
maps stable author IDs to public `name`, archive `slug` and optional approved
public URL. `data/legacy-comments/<article_id>.json` holds the approved original
comments and parent IDs for static thread rendering. Author, category, tag and
date archives are implemented. [The migration guide](docs/migration.md) describes
the public projection and its source/hash manifest.

The author guide documents draft preparation and manual translation review;
those editorial fields are not enforced by the current checks. Each feed emits
up to ten full-content articles using stable language-specific GUIDs and original
publication dates; draft translations stay out of production builds. Production
Discourse integration, CI publishing and deployment remain incomplete. A Git push
currently does not deploy an article. A production transition needs separate
approval. Keep raw exports, private email addresses, credentials and operator
data outside this repository and its build inputs.
