# Article discussions

The source contains an optional native Discourse embed. It is disabled by default:

```toml
[params.discourse]
enabled = false
```

The historical comment archive and forum link work independently of this setting.
Historical names, dates, thread relationships and anchors remain static; the site
does not provide a local comment form.

An embed renders only for a non-draft article in a static production build with
the explicit boolean setting `true` and the matching language base URL:

| Language | Required base URL |
| --- | --- |
| Czech | `https://blog.vpsfree.cz/` |
| English | `https://blog.vpsfree.org/` |

Every Hugo server and every other build environment suppresses the embed,
including previews that explicitly request the setting. Drafts always suppress
it. The shared `data/articles.json` entry must contain an absolute HTTPS Czech
article permalink without credentials, port, query or fragment. Both translations
use this exact `discussion_url` as `discourseEmbedUrl`; their own canonical URLs
remain language-specific. Values are serialized as JSON. Builds do not contact
Discourse, create topics or use forum API keys.

When an enabled production article is opened, Discourse's native embed script
loads from `https://discourse.vpsfree.cz/`. Its normal URL-based flow can create
the missing topic on the first visit, before anyone replies. Publishing an article
does not require a separate per-article forum action after initial setup. Both
languages share the Czech source URL and therefore the intended discussion
identity. The installed forum's behavior has not yet been verified.

## Requirements before enabling

This source candidate grants no authority to change forum settings or production
serving. Keep the setting off until the forum setup and blog transition have
separate approval and these checks have passed:

- Inspect the deployed Discourse version, existing matching topics and any feed
  importer. Verify one topic under concurrent first visits from both languages.
- Configure the exact Czech source host and anchored article-path allowlist,
  excluding previews, feeds, administration, assets and query URLs. These restrict
  import sources; they do not authenticate the calling website. Anyone can trigger
  import of an allowed public article. Verify redirect/private-address safeguards
  against the installed version and keep source canonicals on the public blog.
- Select and verify the proposed public Blog category, import identity,
  notifications and ordinary create/reply permissions. Preserve existing account,
  signup and moderation rules. An archive crawl can create many topics.
- Verify source extraction and links to both translations. Confirm public iframe
  reading from `blog.vpsfree.org`, its frame/referrer requirements and top-level
  forum login/reply navigation under cross-site cookie restrictions. Shared
  `.cz`/`.org` login cookies are not assumed.
- Complete the hosting, alias/feed/media, recovery and separately approved blog
  transition checks. Preserve the shared discussion identity and new forum replies
  during rollback; reverting the static site must not discard forum data.

`nix develop -c bin/check` covers disabled and opt-in rendering using isolated local
content and static outputs. It performs no forum requests. Browser verification
of an enabled candidate must use synthetic origins and blocked requests until
the separate forum integration work is authorized. Never open a locally enabled
production candidate against the actual forum merely to inspect its appearance.
