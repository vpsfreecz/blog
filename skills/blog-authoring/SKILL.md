---
name: blog-authoring
description: Proofread, translate and prepare Czech and English articles as drafts, unlisted review copies or published posts.
---

# Blog authoring

Read [AGENTS.md](../../AGENTS.md) and the canonical
[author guide](../../docs/authoring.md). Use this workflow in an ordinary clone;
no external skill registry or development workspace is required.

1. Establish the factual sources, actual author and requested state: draft,
   unlisted review copy or published article. Start from either Czech or English.
   Automatically correct title and prose typos in context. Preserve technical
   meaning, commands, code, links, proper names, chronology and attribution.
   Never invent facts, personal experience or private authorship.
2. Complete both `index.cs.md` and `index.en.md` in one stable dated bundle,
   including for committed drafts. Imports keep their existing `.html` files.
   Automatically generate the missing language, then compare meaning and archive
   voice. Apply the guide's metadata rules: immutable ID, explicit root URLs,
   shared public authors, Czech discussion URL and per-language feed GUIDs.
   Preserve original archive identity and genuine human-review history.
3. Set the same boolean flags in both files. Draft uses `draft = true` without
   unlisted. An unlisted review copy uses `draft = false` and
   `params.unlisted = true`. Published uses `draft = false` without unlisted.
   Never combine draft and unlisted. An unlisted copy is available to anyone with
   the URL, has a review notice and noindex, and is excluded from discovery and
   discussion embeds. It provides no access restriction.
4. Draft and unlisted dates may change. To publish, clear unlisted and set the
   actual announcement date in both files. Once published, keep the date and
   published state. Keep the bundle, URLs, article ID and GUIDs stable throughout.
   Update `lastmod` for substantive edits or promotion; do not advance dates on
   builds or introduce separate schedule/build/sitemap overrides.
5. Proofread grammar, titles, technical meaning and translation yourself.
   Hunspell reports unknown words and cannot prove grammar or translation quality.
   Finalize Czech, calculate the SHA-256 of its complete exact bytes and record
   it in English. Name the actual reviewer or agent and timestamp truthfully.
   Mark English reviewed only after this work, before sharing unlisted or
   published content. Never fabricate human approval.
6. Run `nix develop -c bin/check-articles`, optionally with article IDs to focus
   spelling. Correct errors or justify precise technical wordlist entries.
   Optional `nix develop -c bin/preview` includes working drafts, even an
   incomplete pair or a future-dated draft. Restart and reload after editing.
   Follow managed-host service-registration rules where applicable.
7. Stage only intended files, inspect `git diff --cached`, and run
   `nix develop -c bin/check-articles --staged`. Install and verify the ordinary
   hook using the guide, preserving existing hooks. It validates the actual index
   and companions; an unstaged correction cannot fix a staged error. A failed
   check blocks commit without stashing, staging or building the site.
8. When the user asks to share unlisted or publish, commit on fresh `main` with
   normal hooks and protections, then push `main`. Commit and push drafts on a
   feature branch. Unlisted and published articles need no feature-branch CI
   cycle first. Include only the intended article changes. Respect Git host
   refusals; do not weaken protections or initialize an empty remote without
   direction.
9. Run `nix develop -c bin/observe-publication --sha <pushed-SHA> --article <ID>`
   for unlisted or published content. It checks both languages' expected state;
   unlisted requires its review notice/noindex, while published must have neither.
   For a draft feature push use
   `nix develop -c bin/observe-publication --sha <pushed-SHA> --branch <feature-branch>`.
   Feature success requires successful checks and skipped deployment; report that
   publication was not requested. Never look for a draft on the public site.
   Report the exact SHA, run/attempt and build/deploy result, or the limited
   site-only fallback. Unknown CI, skipped delivery and timeouts are not confirmed
   publication; without matching built bytes, site appearance cannot prove the
   deployed commit. Inform the user of success or failure. Never automatically
   retry a push/upload or change settings, services, credentials, forum topics or
   publication pause.

Keep private exports and unapproved personal data out of source and build inputs.
Shared metadata additions preserve the original archive projection. Full site
checks/builds remain available as documented; they do not replace contextual
proofreading. Build unlisted source with compatible templates and checks when
reverting code; older templates can expose review copies in listings. Routine
article publication does not authorize server deployment or integration of
unrelated changes carried on an existing branch.
