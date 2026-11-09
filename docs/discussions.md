# Article discussions

The source contains an optional native Discourse embed. It is disabled by default:

```toml
[params.discourse]
enabled = false
```

The historical comment archive and forum link work independently of this setting.
Historical names, dates, thread relationships and anchors remain static; the site
does not provide a local comment form.

An embed renders only for a published article in a static production build with
the explicit boolean setting `true` and the matching language base URL:

| Language | Required base URL |
| --- | --- |
| Czech | `https://blog.vpsfree.cz/` |
| English | `https://blog.vpsfree.org/` |

Every Hugo server and every other build environment suppresses the embed,
including previews that explicitly request the setting. Draft and unlisted pages
suppress the embed; unlisted pages also omit the discussion invitation. Existing
archived comments remain intact. The shared `data/articles.json` entry must
contain an absolute HTTPS Czech article permalink without credentials, port, query or fragment. Both translations
use this exact `discussion_url` as `discourseEmbedUrl`; their own canonical URLs
remain language-specific. Values are serialized as JSON. Builds do not contact
Discourse, create topics or use forum API keys.

When an enabled production article is opened, Discourse's native embed script
loads from `https://discourse.vpsfree.cz/`. Its normal URL-based flow can create
the missing topic on the first visit, before anyone replies. Publishing an article
does not require a separate per-article forum action after initial setup. Both
languages share the Czech source URL and therefore the intended discussion
identity. Forum setup and live behavior must be verified before enabling it.

## Configure the forum

The following steps change forum settings and can create topics. The forum
operator performs them while the blog setting remains `false`.

This procedure follows the configured [Discourse v2026.9.1 source][source], whose
source NAR hash is `sha256-j3JjLYNcv3lluoCekyUUKMfkSX/ExeDsa8zrQ+pDrwg=`.
Check the installed version before relying on its field names, path matching and
framing behavior. Configuration defaults do not prove the current mutable forum
settings; values saved through the forum UI can override them.

### Existing discussions and category

Inspect existing discussions and their source-URL mappings before allowing
imports. The bundled RSS polling plugin defaults to disabled; check the actual
`rss_polling_enabled` setting and feeds at `/admin/plugins/rss_polling`. It uses
`TopicEmbed` too. Matching normalized source URLs can reuse an existing topic,
while alternate URLs or ordinary topics without a mapping can produce duplicates.
A second importer can also update an existing topic's content, author or tags.
Select native first-view creation as the sole creator for this blog after
reconciling those records. The IRC bot's blog feed poll is a separate consumer.

Choose a publicly readable category, such as Blog, and verify its ID and ordinary
member read/reply permissions. Set **Username for topic creation**
(`embed_by_username`) to the existing admin account used as the fallback author.
Preserve signup, login and moderation rules. Match existing topics by their source
URL rather than title. Resolve any missing or ambiguous source mapping before
using that article in the pilot; preserve the topic and its replies.

### Source hosts and paths

Open `/admin/customize/embedding`. Use **Add host**, **Allowed hosts**,
**Path allowlist**, **Post to category** and **Post author**. The stored fields
are `host`, `allowed_paths`, `category_id` and `user`; the form also supports
**Topic tags**. Verify the selected category: an invalid or blank category can
fall back to uncategorized. Leave **Post author** blank on both blog hosts so the
article metadata can select its author. A value here overrides both the metadata
and the global fallback. Preserve unrelated host entries.

Article heads contain the public author names in `author`. The optional
`data/discourse-authors.json` maps existing author IDs to confirmed lowercase
Discourse usernames. Articles with one mapped author put that username in
`discourse-username`. Unmapped and multi-author articles emit the same tag with
empty content. The tag's presence prevents Discourse from treating the public
name as a username, so it uses the configured fallback instead. Keep all names
in a multi-author byline; do not select the first coauthor as the topic owner.

Adding metadata does not migrate existing forum topics. Check their source
mappings and intended ownership before importing or refreshing them. The metadata
also does not enable the embed.

Add exact host `blog.vpsfree.cz`. For normal operation, use this anchored rule
for current and future lowercase root-slug article paths:

```text
\A/(?!(?:feed|search|author|authors|category|categories|tag|tags|archive|archives|page|posts|assets|images|pagefind|admin|login|logout|robots|sitemap)/|wp-|[0-9]+/)[a-z0-9]+(?:-[a-z0-9]+)*/\z
```

This namespace excludes reserved roots, numeric archives, nested paths and
queries. New articles must keep their Czech source path in this namespace. Add
an exclusion before introducing another nonarticle root. Preserve existing
discussion URLs when titles, translations or source folders change.

The pinned host model checks the Ruby regex against both encoded and decoded
path plus query. A blank rule allows every path; rules are not automatically
anchored. Encoded spellings that decode to an allowed slug can match. The rule
does not enforce HTTPS: keep authoritative `discussion_url` values as exact
public HTTPS Czech permalinks, without query, port or fragment. These rules
restrict import sources; they do not authenticate the calling website. Anyone
can trigger import of an allowed public article. Keep redirects and canonicals
on the public blog and retain Discourse's private-address safeguards.

Add exact host `blog.vpsfree.org` with **Path allowlist** `\A(?!)\z`, using the
same verified category and a blank **Post author**. This rule rejects every
English import URL.
The pinned forum includes all registered hosts in CSP `frame-ancestors`
independently of their path rules, so the English host row permits framing of
the shared Czech discussion. Keep `embed_any_origin=false` and
`content_security_policy_frame_ancestors=true`. Verify both framing and rejected
English imports on the installed version; retain HTTPS origin referrers and
avoid wildcard origins or disabling CSP.

### Extraction and visibility

The Discourse deployment manages the settings below through the existing NixOS
`services.discourse.siteSettings` option, including `embed_by_username` from the
configured admin username. Host entries, category selection and permissions
remain in the forum UI. Nix supplies defaults; values saved through the UI take
precedence. When using this deployment, leave these settings in Nix and verify
the effective values after deployment rather than entering them again in the UI.

For a separately managed forum, in **Crawlers configuration**, set
`allowed_embed_selectors` to `.entry-content`.
The static article body has that wrapper; historical comments, navigation and
discussion controls are outside it. Leave `blocked_embed_selectors` empty unless
an observed extraction problem calls for a specific exclusion. Retain these
settings:

| Setting | Value |
| --- | --- |
| `embed_support_markdown` | `false` |
| `embed_truncate` | `true` |
| `embed_full_app` | `false` |
| `embed_set_canonical_url` | `false` |
| `embed_unlisted` | `false` |
| `import_embed_unlisted` | `true` |

`import_embed_unlisted` is a separate site setting, not a field saved by the
embedding editor's **Posts & topics configuration**. With these values, the
topic is created on first view but remains unlisted until a regular reply.
Unlisted topics are not private. Disabling `embed_unlisted` alone does not list
imported topics while `import_embed_unlisted` is true.

Unlisted also does not mean silent. Native import can enqueue alerts. Inspect
category notification defaults, existing member subscriptions, mailing-list
behavior and forum-to-IRC or other webhook notifications before the pilot.
Do not crawl or mass-open the archive to seed topics, and do not change global
notification or account policy automatically.

## Pilot and enable

1. Complete the [hosting and release prerequisites](deployment.md), including
   the English HTTPS host. Keep the embed off through the initial static-site
   switch. WordPress markup does not prove extraction of the final static page.
2. Select one published Czech article with a reconciled source mapping for the
   pilot. Keep the English reject-all row in place. You may temporarily restrict
   the Czech rule to this one path, but that restriction is not required for
   normal operation. On a desktop browser, open `/admin/customize/embedding`, choose
   **Hosts**, and expand **Configuration snippet**. Keep **Full app mode** off.
   In a separate tab, open the selected final static Czech article. In the
   browser's developer tools, use **Elements** to add
   `<div id="discourse-comments"></div>` inside that page's `#respond` section.
   In **Console**, run only the JavaScript inside the generated snippet's
   `<script>` element, replacing `EMBED_URL` with the exact shared Czech
   `discussion_url`. Retain `discourseUrl: 'https://discourse.vpsfree.cz/'`.
   This deliberately loads the [native iframe loader][native-loader] and can
   create a topic and notifications. It changes only that tab's temporary DOM;
   leave source files, served HTML and the blog's `enabled = false` unchanged.
3. Repeat the same steps in a tab on the paired English article, using the same
   Czech `EMBED_URL`. For a concurrent check, prepare one tab per production
   origin and run that same snippet in both. Limit this to the pilot article;
   do not open the archive. Record the single topic URL and verify the extracted
   prose, code, images and links from the static Czech page. Check anonymous
   reading, ordinary authenticated reply through top-level forum navigation,
   notifications and English iframe CSP/referrer behavior. Test cross-site
   cookie restrictions; shared Czech/English login cookies are not assumed.
   Reloading discards the temporary DOM changes. Keep previews and drafts
   isolated from the production forum.
4. After setup, mappings and the pilot are accepted, apply the final Czech path
   rule above. Through the ordinary reviewed protected-main artifact and content
   release, change only the production opt-in in `hugo.toml`:

   ```toml
   [params.discourse]
   enabled = true
   ```

Keep all existing environment, base-URL, draft and server guards. Future articles
within the source-path namespace need no per-article forum action. Record the
observed version, category, author, settings and pilot results in the operator's
rollout record. Listed-on-first-view behavior would require a separate deliberate
change to both visibility settings after reviewing notification effects.

`nix develop -c bin/check` covers disabled and opt-in rendering using isolated local
content and static outputs. It performs no forum requests. Browser verification
of a local candidate must use synthetic origins and blocked forum requests.
Loading an enabled production embed is not a read-only appearance check.

## Stop imports or recover

Disable the blog embed through the normal content release. To stop new imports
immediately, the operator can narrow the affected source-host path rule through
the forum UI while keeping the host row needed for framing. Keep direct forum
links and preserve every topic, source mapping, reply and archived comment.

For a blog cutover failure, follow the [hosting recovery procedure](deployment.md)
to restore the retained WordPress route. Do not roll back or delete the forum
database. Record new articles or forum replies that WordPress cannot consume
automatically.

The version-sensitive behavior above comes from the pinned source's
[host matcher][host], [host editor][host-editor], [embedding settings][settings],
[CSP framing rules][csp], [topic importer][importer] and
[reply visibility handling][visibility]. The [RSS plugin][rss] shares the native
topic mapping. These source references do not establish live forum settings or
replace the operator's pilot.

[source]: https://github.com/discourse/discourse/tree/v2026.9.1
[host]: https://github.com/discourse/discourse/blob/v2026.9.1/app/models/embeddable_host.rb
[host-editor]: https://github.com/discourse/discourse/blob/v2026.9.1/app/controllers/admin/embeddable_hosts_controller.rb
[settings]: https://github.com/discourse/discourse/blob/v2026.9.1/config/site_settings.yml
[csp]: https://github.com/discourse/discourse/blob/v2026.9.1/lib/content_security_policy/default.rb
[importer]: https://github.com/discourse/discourse/blob/v2026.9.1/app/models/topic_embed.rb
[visibility]: https://github.com/discourse/discourse/blob/v2026.9.1/lib/post_jobs_enqueuer.rb
[rss]: https://github.com/discourse/discourse/tree/v2026.9.1/plugins/discourse-rss-polling
[native-loader]: https://github.com/discourse/discourse/blob/v2026.9.1/public/javascripts/embed.js
