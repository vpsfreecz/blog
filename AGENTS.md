# Blog development and authoring

Read [README.md](README.md) for build contracts and
[docs/authoring.md](docs/authoring.md) before writing or translating an article.
Any agent can read [the authoring skill](skills/blog-authoring/SKILL.md) directly;
it needs no installation or external workspace.

- Use the pinned environment: `nix develop -c bin/check` and `nix build .#site`.
  Install the ordinary pre-commit hook as described in the author guide; preserve
  an existing hook setup. It checks the actual index without building the site.
- Start drafts in `content/posts/YYYY-MM-DD-english-title/index.cs.md`; add
  `index.en.md` in the same bundle. Choose an independent immutable article ID
  outside `wp-`; the folder name does not identify the article. Follow the
  dated-folder rules in `docs/authoring.md`.
  Imported articles use `index.cs.html` and `index.en.html`; preserve their HTML
  structure and code. Keep `translationKey` and `params.article_id` identical.
- Keep Czech and English at their separate production host roots. Preserve
  published paths, original dates, shared bylines, feed identities and the
  original Czech `discussion_url`. Never infer identity from a translated title.
- Preview real drafts with `nix develop -c bin/preview`. `--fixtures` selects
  the isolated synthetic demo. Preserve approved historical media iframes;
  production Discourse scripts and comment embeds remain disabled.
  Follow the host's service-registration rules if working in a managed environment.
- Accept either Czech or English as the starting text. Proofread both languages
  in context and preserve technical facts, commands, links and attribution.
  Commit a complete CS/EN pair, including drafts. Finalize Czech before hashing
  its exact file bytes into the English review record. Name the actual reviewer
  or agent; preserve genuine historical human-review fields. Run
  `nix develop -c bin/check-articles --staged` before committing. Hunspell reports
  unknown words; it does not certify grammar, meaning or translation quality.
- Keep private exports, credentials, user records and unapproved personal data
  outside the repository and its build inputs. Synthetic fixtures stay draft-only.
- Git host write permissions and branch protections control publication
  access. When the user asks to publish a ready article, use fresh `main` with
  ordinary hooks and protections. Drafts and preparation stay on a feature
  branch. Include only the intended article changes and respect host permissions.
  Observe the exact pushed article SHA with `bin/observe-publication` as described
  in the guide. The workflow prepares release artifacts.
  Target publication defaults off; an operator must enable and resume its
  installed policy before protected-main push builds can publish through
  authenticated upload. Feature pushes run checks only; system deployment
  and public cutover are operator steps. Do not initialize an empty remote without
  maintainer direction. Imported articles, historical comments and
  full-content feeds are implemented. The optional production Discourse embed
  defaults off; forum setup and deployment still need verification and
  approval.
