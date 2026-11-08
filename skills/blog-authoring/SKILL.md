---
name: blog-authoring
description: Proofread, complete and publish paired Czech and English articles using the pinned checks and ordinary Git workflow.
---

# Blog authoring

Read [AGENTS.md](../../AGENTS.md) and the canonical
[author guide](../../docs/authoring.md). Use this workflow in an ordinary clone;
no external skill registry or development workspace is required.

1. Establish the supplied language, factual sources, actual author and requested
   publication scope. Either Czech or English can be the starting text.
   Automatically correct title and prose typos in context, preserving technical
   meaning, commands,
   code, links, proper names, chronology and attribution. Never invent facts,
   personal experience or private authorship.
2. Complete both `index.cs.md` and `index.en.md` in one stable dated bundle,
   including for committed drafts. Imports keep their existing `.html` files.
   Automatically generate the missing language, then compare both for meaning
   and archive voice. Apply the author guide's dates, immutable ID, explicit root
   URLs, shared public
   authors, Czech discussion URL and per-language feed GUIDs. Preserve original
   archive identity and existing human-review history.
3. Finalize Czech, calculate the SHA-256 of its complete exact bytes, and record
   it in English. Review grammar, title/prose spelling, technical meaning and
   translation yourself; Hunspell only reports unknown words. Name the actual
   reviewer or agent and timestamp truthfully. Set `translation_status=reviewed`
   only after that work; never fabricate human approval. Keep both variants draft
   while preparing them.
4. Run `nix develop -c bin/check-articles`, optionally with article IDs to focus
   spelling. Correct errors or justify precise technical wordlist entries; do not
   bulk-whitelist legacy prose. Unknown-word checks cannot prove grammar or
   translation quality. For an optional preview, run
   `nix develop -c bin/preview`. It includes working drafts, even an incomplete
   pair. Restart and reload after editing. Follow
   managed-host service-registration rules where applicable.
5. Stage only intended files, inspect `git diff --cached`, and run
   `nix develop -c bin/check-articles --staged`. Install/verify the ordinary hook
   using the guide, preserving an existing hook setup. It validates the actual
   index and companions; an unstaged correction cannot fix a staged error. A
   failed check blocks commit without stashing, staging or building the site.
6. When the user asks to publish a ready article, commit directly on fresh `main`
   with normal hooks and protections, then push `main`. Commit and push drafts
   and preparation on a feature branch. A ready article does not need a feature-branch
   CI cycle. Include only the intended article changes. Respect Git host refusals;
   do not weaken protections or initialize an empty remote without direction.
7. Run `nix develop -c bin/observe-publication --sha <pushed-SHA> --article <ID>`.
   For a draft feature push, use
   `nix develop -c bin/observe-publication --sha <pushed-SHA> --branch <feature-branch>`
   instead. Feature success requires successful checks and skipped deployment;
   report that publication was not requested. Never check a draft on the public
   site. Report unknown CI or timeouts as unverified, and unexpected feature
   deployment as a policy mismatch.
   Report exact SHA, run/attempt and terminal build/deploy result or the bounded
   site-only fallback. Skipped/failed delivery or unknown CI is not success;
   without exact built bytes, site appearance does not prove the deployed commit.
   Report failures and timeouts to the user. Never retry a push/upload or change
   settings, services, credentials, forum topics or publication pause automatically.

Keep private exports and unapproved personal data out of source and build inputs.
Shared metadata additions preserve the original archive projection. Full site
checks/builds remain available as documented; they do not replace contextual
proofreading. Routine article publication does not authorize server deployment
or integration of unrelated changes carried on an existing branch.
