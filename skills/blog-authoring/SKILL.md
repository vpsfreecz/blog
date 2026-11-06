---
name: blog-authoring
description: Prepare and review Czech blog drafts and English translations in this repository using its pinned Hugo environment and Git workflow.
---

# Blog authoring

Read [AGENTS.md](../../AGENTS.md) and the canonical
[author guide](../../docs/authoring.md). This Markdown workflow works in an
ordinary clone; it requires no skill registry or external development workspace.

1. Establish the requested article, factual sources, actual author and languages.
   Preserve technical meaning, commands, links and chronology. Use direct prose;
   never invent facts, first-person experiences or an author's attribution.
2. Prepare `content/posts/<article_id>/index.cs.md` as a draft. New IDs must stay
   outside `wp-`. Use explicit stable paths, original dates, and identical
   `translationKey`/`params.article_id` in both language variants. Add shared
   public authors, the original absolute Czech `discussion_url` and immutable
   per-language `feed_guids` as described in the guide.
3. Add English in `index.en.md` without altering the Czech source. Keep it a
   draft until a human reviews meaning and voice. Imported articles instead use
   `index.cs.html` and `index.en.html`; preserve HTML/code/links and translate
   visible prose. Record translation status, the SHA-256 of the complete current
   Czech `.md` or `.html` file, reviewer and review timestamp; re-review source
   changes.
   These records are not enforced by the current checks.
4. Preview real drafts with `nix develop -c bin/preview`; use `--fixtures` only
   for the isolated demo. Check both pages, bylines, images, code and reciprocal
   language links. Historical comments and approved media iframes are supported;
   production Discourse embeds remain disabled. Follow host service-registration
   rules in managed environments.
5. Run `nix develop -c bin/check` and `nix build .#site`. Inspect the diff and
   production output. Keep private exports, credentials and unapproved personal
   data outside source and build inputs. Do not create forum topics or request
   forum credentials while authoring.
6. Prepare publication only within the requested scope and Git host permissions.
   Follow branch protections and editorial review; set `draft=false` only for an
   approved variant, and commit intended files with ordinary hooks. Do not
   initialize an empty remote without maintainer direction. Full-content RSS
   uses stable per-language identities and excludes drafts in production builds.
   Actions publishing and production Discourse integration are not implemented,
   so pushing a commit currently does not make an article live.
