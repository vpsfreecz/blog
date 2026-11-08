# Writing and translating articles

This repository builds Czech at `https://blog.vpsfree.cz/` and English at
`https://blog.vpsfree.org/`. Each language has its own host root. You can prepare
and preview a draft from an ordinary clone with Git and Nix. When an agent writes
an article, it corrects title and prose typos and supplies the missing language
automatically. Review both versions for meaning before committing.

## Prepare a draft

Clone `git@github.com:vpsfreecz/blog.git`, enter the clone and read
[AGENTS.md](../AGENTS.md). On an initialized repository, create a working branch
for drafts or preparation, for example `git switch -c article/network-update`.
Approved ready articles follow the main-branch publication steps below. If the
remote is empty, a maintainer must direct its initial default branch.

Choose an immutable article ID outside the reserved imported `wp-` namespace,
such as `post-2026-11-network-update`. Create
`content/posts/2026-11-06-network-update/index.cs.md` with a text editor, or start
with `index.en.md` if the supplied text is English. Complete the other language
before committing, even for a draft. A single-language working draft can still be
previewed. The following is a metadata example, not a real article:

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
identity. Uncommitted previews can omit a translation. Every committed article,
including a draft, needs exactly one Czech and one English variant with the same
draft state and original date. An English URL never substitutes Czech content
for a missing translation.

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

Keep both pages at `draft = true` while preparing them. Proofread titles and
prose in context, then compare meaning, commands/code, links, chronology,
attribution and voice across the two languages. Either language can be the
starting text; finalize Czech before calculating the complete-file hash recorded
in English. After review, set `translation_status = "reviewed"`, name the actual
reviewer or agent in `translation_reviewed_by`, and record an RFC3339
`translation_reviewed_at`. Preserve genuine historical review provenance and
never claim human approval for an agent review. Re-review after a Czech
source change and refresh the English source hash. The article checker validates
these records and source freshness; it cannot perform the contextual review.

Use direct practical English, familiar technical terms and short paragraphs.
Lead with what is available or has changed and how to use it. Preserve the
original author's facts and viewpoint. Retain first-person claims only when
supported by the source; do not invent experiences, jokes or promises. Keep
the source facts intact when correcting either language. For Czech member-facing
instructions, address one reader informally and use standard spelling and
typography.

Style references include the [mailing-list archive](https://lists.vpsfree.cz/mailman3/hyperkitty/list/news-list@lists.vpsfree.cz/latest)
and [announcements category](https://discourse.vpsfree.cz/c/announcements/5).
Specific examples are the [primary DNS announcement](https://discourse.vpsfree.cz/t/primarni-dns-servery-primary-dns-servers/258)
and [initial VPS configuration announcement](https://discourse.vpsfree.cz/t/prvotni-konfigurace-vps-skriptem-cloud-init-a-nixos-initial-vps-configuration-with-script-cloud-init-and-nixos/317).
The collections contain multiple authors; a style reference never changes the
article's byline. Contextual review covers voice as well as technical meaning.

## Check the staged articles

Install the repository's ordinary hook only if the clone has no existing hook
setup. Inspect `git config --get core.hooksPath` first; preserve an existing
configuration and arrange for it to call the same staged check.

```sh
git config --local core.hooksPath .githooks
git config --get core.hooksPath
test -x .githooks/pre-commit
```

The hook runs `nix develop -c bin/check-articles --staged`. A failed check blocks
the commit. It reads article and shared-metadata blobs from the actual index,
including the other language when only one file was staged. An unstaged fix does
not repair staged content, and an unstaged mistake does not replace a good index.
The hook does not stage files, stash changes or build the site.

Plain `nix develop -c bin/check-articles` checks working source. To focus spelling
diagnostics, pass article IDs, for example:

```sh
nix develop -c bin/check-articles post-2026-11-network-update
```

Pairing, TOML, dates, URLs, authors, taxonomies, immutable identities and source
hashes are still validated. Original archive rows remain audited; new unrelated
shared-metadata rows do not require changing their recorded import digests.

Pinned Hunspell Czech and English dictionaries report unknown title/prose words
for new articles and introduced words in edited articles. Code, URLs and markup
are excluded; visible link labels and image descriptions are included. Correct
real errors, or justify a specific technical term in `tools/spelling-cs.txt` or
`tools/spelling-en.txt`. Do not whitelist an article's errors to make a check pass.
Unchanged legacy prose is not a new spelling-cleanup requirement. Unknown-word
checks cannot prove grammar, translation quality or the absence of valid-word
typos; contextual proofreading is still required.

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
private-data exclusions. Set `draft = false` on both variants only for approved
ready content, with reviewed English and its current Czech source hash. Stage
only intended article/shared-metadata files, inspect `git diff --cached`, and run
`nix develop -c bin/check-articles --staged` before the ordinary commit. The
contextual review must be complete before marking English reviewed.

For an article the user has asked to publish, start from fresh `main`, commit
with ordinary hooks and push `main` within Git host permissions and protections.
Keep drafts and preparation on a feature branch. A ready article does not need
a feature-branch CI cycle before publication. Publish only the intended article
changes; keep unrelated feature work separate. Respect a host refusal and obtain
maintainer direction before initializing an empty remote. System deployment,
publication settings and public cutover remain separate maintainer operations.

Observe the exact pushed SHA and article ID:

```sh
nix develop -c bin/observe-publication --sha <pushed-SHA> --article <article-ID>
```

The read-only observer follows only that SHA's main-push Build blog run, including
build and deploy jobs, with a default ten-minute bound. Failed or skipped delivery
is not publication success. It never retries a push/upload or resumes publication.
The observer first uses the public GitHub API. It can also use an existing `gh`
login; it does not require a new login or secret. If CI cannot be observed,
bounded CS/EN site checks report only title/article/canonical observations and
explicitly leave CI
and the deployed commit unproven. For byte comparisons, supply an existing build
from the exact pushed source with `--artifact PATH`. Report the pushed SHA,
run/attempt and result or limited fallback, including any timeout.

For a draft pushed to a feature branch, observe checks on that exact branch:

```sh
nix develop -c bin/observe-publication --sha <pushed-SHA> --branch <feature-branch>
```

Feature success means the workflow and build passed and deployment was skipped.
The observer reports that publication was not requested. It makes no public-site
requests for a draft; unavailable CI or a timeout stays unknown. Unexpected
feature deployment is a policy mismatch. Report the check result to the user
without claiming the draft is live.

The workflow prepares [release artifacts](deployment.md). Target publication
defaults off; after an operator enables and resumes its installed policy,
protected-main pushes can publish validated content through authenticated upload.
Feature pushes run checks only. Article writing does not grant forum, server,
credential or environment-setting changes.
