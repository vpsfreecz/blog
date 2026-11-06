# Blog development and authoring

Read [README.md](README.md) for build contracts and
[docs/authoring.md](docs/authoring.md) before writing or translating an article.
Any agent can read [the authoring skill](skills/blog-authoring/SKILL.md) directly;
it needs no installation or external workspace.

- Use the pinned environment: `nix develop -c bin/check` and `nix build .#site`.
  Use the repository's Git hooks if a framework is introduced; none is declared.
- Start articles as drafts in `content/posts/<article_id>/index.cs.md`; add
  `index.en.md` for a translation. Use a new immutable ID outside `wp-`.
  Imported articles use `index.cs.html` and `index.en.html`; preserve their HTML
  structure and code. Keep `translationKey` and `params.article_id` identical.
- Keep Czech and English at their separate production host roots. Preserve
  published paths, original dates, shared bylines, feed identities and the
  original Czech `discussion_url`. Never infer identity from a translated title.
- Preview real drafts with `nix develop -c bin/preview`. `--fixtures` selects
  the isolated synthetic demo. Preserve approved historical media iframes;
  production Discourse scripts and comment embeds remain disabled.
  Follow the host's service-registration rules if working in a managed environment.
- Preserve technical facts, commands, links and attribution. English translations
  stay drafts until a human reviews meaning and voice against the current Czech
  file; hash its exact bytes, using the current `.md` or `.html` extension, and
  record the reviewer fields described in the author guide.
  These fields require manual review; checks do not enforce them yet.
- Keep private exports, credentials, user records and unapproved personal data
  outside the repository and its build inputs. Synthetic fixtures stay draft-only.
- Git host write permissions and branch protections control publication access.
  Follow the requested branch/review policy; never assume an agent can grant
  itself push permission. Actions publishing is not implemented: pushing a commit
  does not deploy the site. Do not initialize an empty remote without maintainer
  direction. Imported articles, historical comments and full-content feeds are
  implemented; production Discourse integration and deployment remain incomplete.
