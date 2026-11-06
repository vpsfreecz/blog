# Blog development

Read [README.md](README.md) for the source and artifact contracts.

- Use the pinned shell: `nix develop`. Run `bin/check` before committing.
- Keep Czech and English at their separate host roots; do not add locale paths.
- Preserve explicit article URLs, stable IDs, bylines and the shared original
  Czech discussion URL. Translation canonicals stay language-specific.
- Keep synthetic fixtures isolated and draft-only. Never put private exports or
  credentials in source, fixtures or public artifacts.
- Production Discourse integration, imported content, feed compatibility and
  publication automation require their own completed packages. Keep previews
  free of production embed scripts and iframes.
- Use ordinary Git hooks when a framework is introduced; none is declared here.
