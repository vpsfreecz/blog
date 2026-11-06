# Writing and translating articles

This repository builds Czech at `https://blog.vpsfree.cz/` and English at
`https://blog.vpsfree.org/`. Each language has its own host root. You can prepare
and preview a draft from an ordinary clone with Git and Nix; no development
workspace, session record or installed agent skill is required.

## Prepare a draft

Clone `git@github.com:vpsfreecz/blog.git`, enter the clone and read
[AGENTS.md](../AGENTS.md). On an initialized repository, create a working branch
according to its contribution policy, for example `git switch -c article/network-update`.
If the remote is empty, a maintainer must direct its initial default branch.

Choose an immutable article ID outside the reserved imported `wp-` namespace,
such as `post-2026-11-network-update`. Create
`content/posts/post-2026-11-network-update/index.cs.md` with a text editor.
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
`discussion_url`. Never replace it with the English or preview URL. Article
writing needs no forum credentials or manual topic-creation step; native
Discourse integration is planned but not implemented.

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

Under the English file's `[params]`, record the editorial state:

```toml
translation_status = "draft"
translation_source_sha256 = "<SHA-256 of the complete current Czech file bytes>"
```

Calculate that hash after finalizing the Czech source:

```sh
nix develop -c python3 -c 'import hashlib,pathlib; print(hashlib.sha256(pathlib.Path("content/posts/post-2026-11-network-update/index.cs.md").read_bytes()).hexdigest())'
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
the isolated synthetic demo instead. `--help` lists preview options. The VPN
mode is intended for a configured review host, not a requirement for authoring.
In a managed environment, follow that host's temporary-service registration
rules. Ordinary clones can run the command directly. Keep drafts on loopback
unless sharing them was explicitly requested.

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
branch; an agent cannot grant itself permission. Actions publishing is not
implemented yet, so a successful push currently does not deploy an article.
A maintainer must configure and verify the publishing pipeline before Git pushes
can serve as live publication. Do not initialize the remote or perform a server
deployment as part of routine article writing without maintainer direction.
