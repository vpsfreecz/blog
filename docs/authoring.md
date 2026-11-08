# Writing and translating articles

This repository builds Czech at `https://blog.vpsfree.cz/` and English at
`https://blog.vpsfree.org/`. Each language has its own host root. You can prepare
and preview a draft from an ordinary clone with Git and Nix.

## Prepare a draft

Clone `git@github.com:vpsfreecz/blog.git`, enter the clone and read
[AGENTS.md](../AGENTS.md). On an initialized repository, create a working branch
according to its contribution policy, for example `git switch -c article/network-update`.
If the remote is empty, a maintainer must direct its initial default branch.

Choose an immutable article ID outside the reserved imported `wp-` namespace,
such as `post-2026-11-network-update`. Create
`content/posts/2026-11-06-network-update/index.cs.md` with a text editor.
The following is a metadata example, not a real article:

```toml
+++
title = "Síťová novinka"
date = "2026-11-06T12:00:00+01:00"
lastmod = "2026-11-06T12:00:00+01:00"
draft = true
translationKey = "post-2026-11-network-update"
url = "/sitova-novinka/"
[params]
article_id = "post-2026-11-network-update"
+++
```

Use the calendar date stored in the Czech article, without converting its
timezone, followed by the English title slug. Remove apostrophes, normalize with
Unicode NFKD to ASCII, lowercase, and replace runs of non-alphanumeric characters
with a hyphen. If the title yields no slug, use `article-<article_id>`. For a
date/title collision, append `-<article_id>` to every colliding folder. Keep the
assigned folder stable through later title edits; article IDs and public URLs
remain independent.

Write the Markdown body after the closing `+++`. Use the intended original
publication time with an explicit timezone, and update `lastmod` for a material
content change. Do not advance either date just because a build runs. Keep the
article ID and a published URL stable. Use explicit paths with leading and
trailing slashes; do not add `/cs/` or `/en/` to production paths.

Add the article's shared entry to `data/articles.json`, preserving other entries:

```json
{
  "post-2026-11-network-update": {
    "discussion_url": "https://blog.vpsfree.cz/sitova-novinka/",
    "author_ids": ["example-author"],
    "feed_guids": {
      "cs": "urn:vpsfree:blog:post-2026-11-network-update:cs",
      "en": "urn:vpsfree:blog:post-2026-11-network-update:en"
    }
  }
}
```

Reuse a stable author ID from `data/authors.json`, or add an approved public
byline with a stable archive slug, for example
`"example-author": {"name": "Public author name", "slug": "public-author"}`.
Both languages use the same author IDs and the same absolute Czech
`discussion_url`. Never replace it with the English or preview URL. Give a new
Czech article a lowercase root-slug path within the [discussion path rules](discussions.md#source-hosts-and-paths),
and preserve the source URL after publication. Article writing needs no forum
credentials or manual topic-creation step. After the [forum setup and pilot](discussions.md#pilot-and-enable)
and production opt-in, the native embed can create a shared topic on the first
article visit. The source defaults to disabled; drafts and previews always
suppress the embed.

For new articles, assign the per-language URNs shown above once and retain them
through corrections. Imported Czech articles retain their exact original
`https://blog.vpsfree.cz/?p=<sourceID>` GUID; imported English articles use
`urn:vpsfree:blog:wp-<sourceID>:en`. These GUIDs are identifiers, not navigation
URLs. RSS uses `isPermaLink="false"` and emits up to ten full-content articles
with their original publication dates. Production builds exclude drafts.

Put approved article images in `static/images/<article_id>/` and refer to them
with root-relative Markdown links, for example
`![Description of the network diagram](/images/post-2026-11-network-update/diagram.png)`.
Use useful image descriptions and check their display. Raw HTML is disabled in
the current Markdown renderer; do not assume pasted embeds will appear.
Keep private source material, dumps, credentials and unapproved personal data
outside this clone and all build inputs.

## Add or revise English

Create `index.en.md` alongside a new Markdown article's Czech file. Imported
articles use `index.cs.html`; translate them in `index.en.html`, preserving HTML
structure, code, links and media while translating visible prose and image
descriptions. Keep one file per language; do not add a Markdown duplicate of an
existing HTML variant. Give the English variant an English title and
explicit English `url`, such as `/network-update/`. Copy the original `date`,
`translationKey` and `params.article_id`; retain the shared byline and discussion
identity. A missing translation stays absent rather than showing Czech at an
English URL.

Imported English articles keep the original source URLs. During rendering, links
to known blog articles use an English page available in that build, including
drafts in preview; otherwise they lead to the Czech original. Knowledge-base
links use only the verified page and section mappings in `data/english-links.json`.
Unmatched links stay unchanged.

Under the English file's `[params]`, record the editorial state:

```toml
translation_status = "draft"
translation_source_sha256 = "<SHA-256 of the complete current Czech file bytes>"
```

Calculate that hash after finalizing the Czech source:

```sh
nix develop -c python3 -c 'import hashlib,pathlib; print(hashlib.sha256(pathlib.Path("content/posts/2026-11-06-network-update/index.cs.md").read_bytes()).hexdigest())'
```

For an imported article, use its actual `index.cs.html` path instead. Hash the
complete current file, including frontmatter and original line endings. The
import manifest's `cs_file_sha256` identifies that file; the separate
`params.source_body_sha256` identifies the private raw WordPress body and must
not be used as the translation source hash. Approved historical comments remain
in their original language and are shared across both article variants.

Keep the English page's top-level `draft = true` while preparing it. A human
reviewer compares meaning, commands/code, links, chronology, attribution and
voice with the Czech source. After review, set `translation_status = "reviewed"`
and add `translation_reviewed_by` with the reviewer's approved public name or
identifier and `translation_reviewed_at` with an RFC3339 timestamp. Record the
hash of the exact reviewed Czech file. These are manual editorial records;
the current checks do not validate the fields or source freshness. Re-review
English after any Czech source change before publishing the translation.

Use direct practical English, familiar technical terms and short paragraphs.
Lead with what is available or has changed and how to use it. Preserve the
original author's facts and viewpoint. Retain first-person claims only when
supported by the source; do not invent experiences, jokes or promises. Keep
the Czech source intact when adding English. For Czech member-facing instructions,
address one reader informally and use standard spelling and typography.

Style references include the [mailing-list archive](https://lists.vpsfree.cz/mailman3/hyperkitty/list/news-list@lists.vpsfree.cz/latest)
and [announcements category](https://discourse.vpsfree.cz/c/announcements/5).
Specific examples are the [primary DNS announcement](https://discourse.vpsfree.cz/t/primarni-dns-servery-primary-dns-servers/258)
and [initial VPS configuration announcement](https://discourse.vpsfree.cz/t/prvotni-konfigurace-vps-skriptem-cloud-init-a-nixos-initial-vps-configuration-with-script-cloud-init-and-nixos/317).
The collections contain multiple authors; a style reference never changes the
article's byline. Human review covers voice as well as technical meaning.

## Preview and check

From the clone root:

```sh
nix develop -c bin/preview
```

This includes real repository drafts. Open Czech at `http://localhost:1313/`
and English at `http://localhost:1314/`; follow each article's explicit path
and its paired language link. Use `nix develop -c bin/preview --fixtures` for
the isolated synthetic demo instead. `bin/preview --help` lists preview options.
Keep drafts on loopback unless sharing them was explicitly requested.

The preview renders a coherent snapshot of articles and their Pagefind index;
it does not watch edits. Stop it after editing, rerun the same command with the
same flags, and reload the browser. This rebuilds the pages and search together,
including added or removed drafts.

Search from the sidebar or `/search/` on each language's loopback origin. Search
indexes titles and article bodies, including drafts in previews, while excluding
navigation and historical comments. Production builds exclude drafts from both
pages and search. Use the reload action if an old tab can no longer load its
search files after an update.

Inspect the body, byline, dates, images, code and language switch. Then run:

```sh
nix develop -c bin/check
nix build .#site
```

The checks cover article/archive routes, feeds, metadata, isolated fixtures and
reproducible output; they do not replace article or translation review. The production build
excludes drafts and synthetic fixtures. `result/cs/` and `result/en/` are separate
document roots; `metadata.json` remains outside them. Imported HTML and approved
historical comment threads are rendered, and the feeds contain full article
content. Approved historical YouTube/SuperLectures media iframes are retained;
production Discourse comment embeds remain disabled.

## Prepare publication

Review the diff for intended content, public attribution, stable URLs/GUIDs and
private-data exclusions. Set `draft = false` only for a variant approved for
publication; English also requires completed human review and a matching current
Czech source hash. If that edit changes the Czech file, refresh its recorded hash
after checking that the reviewed meaning is unchanged. Re-run checks and inspect
the production output, then commit only the intended files using the repository's
hooks and contribution policy.

Push the working branch only with the Git host's write permission. Follow any
required review and protected-publication-branch policy before advancing that
branch; an agent cannot grant itself permission. The Actions workflow checks
source and packages trusted-main [release artifacts](deployment.md). Target
publication defaults off. After a maintainer enables and resumes the installed
policy, successful protected-main push builds can publish validated content
through authenticated upload. Feature pushes run checks only. System deployment
and public cutover remain maintainer operations. Do not initialize the remote or perform
a server deployment as part of routine article writing without maintainer
direction.
