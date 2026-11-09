# Article discussions

The source contains an optional native full-app Discourse embed for inline
replies. It is disabled by default:

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
retain the original Czech `discussion_url` for provenance and source navigation.
Both translations use the actual published English counterpart at
`https://blog.vpsfree.org/` as their shared `discourseEmbedUrl`. A missing,
unpublished or invalid English counterpart suppresses forum requests. Each
article keeps its own language-specific canonical URL. Builds serialize the
embed values as JSON; they do not contact Discourse, create topics or use API keys.

When someone opens an enabled production article, Discourse's native embed
script loads from `https://discourse.vpsfree.cz/`. It can create a missing topic
on the first visit, before anyone replies. Both languages share that topic,
including its English opening post and source link. Future articles need no
manual topic-creation step after setup. Check forum settings and live behavior
before enabling the embed. Reconcile any existing Czech source mappings first;
changing the source URL does not merge or migrate topics.

## Reply counts on listings

Published articles on listing pages can show Discourse reply counts through one
asynchronous batch request to the forum's `/embed/count` endpoint. Both languages
look up the same English source URL while their discussion links lead to the
local article. Counts use the same production opt-in as the embed. Previews,
drafts and unlisted pages make no count requests. Single-article pages use the
native embed without a separate count request.

Counts include forum replies only; archived WordPress comments remain separate.
Discourse returns a reply phrase in its effective forum/user locale, which may
differ from the blog language. The blog displays that phrase as text beside a
localized Discourse discussion label. It does not change forum locale settings.

Missing or restricted results, script/CSP errors and the five-second deadline
leave a usable plain discussion link. An omitted result never becomes zero;
a returned zero phrase can be displayed. The client makes at most one request
for up to 50 distinct displayed article URLs within an 8 KiB request URL. It
uses no retries, polling, API keys or backend. The deadline limits UI waiting;
it does not guarantee network cancellation or measure forum latency. JSONP
executes code from the fixed forum origin already trusted by the embed.

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

Add exact host `blog.vpsfree.org`. For normal operation, use this anchored rule
for English article paths, including supported nested and underscore paths:

```text
\A/(?!(?:cs|en|search|feed|author|authors|category|categories|tag|tags|archive|archives|page|posts|assets|images|pagefind|admin|login|logout|robots|sitemap)(?:/|\z)|[0-9]{4}/[0-9]{2}(?:/|\z))[a-z0-9]+(?:[-_][a-z0-9]+)*(?:/[a-z0-9]+(?:[-_][a-z0-9]+)*)*/?\z
```

This namespace excludes reserved roots, language prefixes and generated
calendar-month archive paths. It supports the existing English route grammar,
including nested and underscore paths. Keep English article URLs stable; add an
exclusion before introducing another nonarticle root. Original Czech routes and
provenance fields stay unchanged.

Discourse removes the trailing slash from the source URL before matching the
host used to select the import category. Host rules must accept both forms so
the canonical article URL and normalized import URL select the same host entry.

The pinned host model checks the Ruby regex against both encoded and decoded
path plus query. A blank rule allows every path; rules are not automatically
anchored. Encoded spellings that decode to an allowed slug can match. The rule
does not enforce HTTPS. The shared embed source must be the exact public HTTPS
English permalink, without query, port or fragment. The original Czech
`discussion_url` field stays unchanged. These rules
restrict import sources; they do not authenticate the calling website. Anyone
can trigger import of an allowed public article. Keep redirects and canonicals
on the public blog and retain Discourse's private-address safeguards.

Add exact host `blog.vpsfree.cz` with the same verified category and blank
**Post author**, using the existing Czech root-slug rule:

```text
\A/(?!(?:feed|search|author|authors|category|categories|tag|tags|archive|archives|page|posts|assets|images|pagefind|admin|login|logout|robots|sitemap)(?:/|\z)|wp-|[0-9]+(?:/|\z))[a-z0-9]+(?:-[a-z0-9]+)*/?\z
```

Full-app mode checks the parent referrer against host path rules as well as CSP.
Both article-path rules are needed; a Czech reject-all framing row would block
full-app display. Keep `embed_any_origin=false`,
`content_security_policy_frame_ancestors=true`, exact hosts and HTTPS referrers.
The blog supplies only the shared English source during ordinary browsing.
Native allowlists also permit manual or external Czech-source imports, which
could create a separate topic; they do not enforce English-only topic identity.
Reconcile existing mappings before enabling, preserving topics and replies.

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
| `embed_full_app` | `true` |
| `embed_set_canonical_url` | `false` |
| `embed_unlisted` | `false` |
| `import_embed_unlisted` | `true` |

The blog sends native `fullApp: true`; the server setting must also be true.
Discourse uses its default 600-pixel iframe height, lazy loading and scrolling.

The Nix configuration sets `security.same_site_cookies = "None"` to support
cross-site iframe sessions on `blog.vpsfree.org`. This changes the cookie default
for the whole forum. The existing HTTPS configuration supplies Secure session
cookies; CSRF, origin and CSP protections stay enabled. Verify those effective
settings after deployment.

Native sign-in may open a top-level tab and use the Storage Access API.
SameSite=None does not override browser cookie blocking or guarantee storage
access. Keep the top-level forum link available when embedded login is blocked.
Verify login and inline replies from both blog hosts during the authorized pilot;
source checks cannot establish browser authentication.

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
2. Select one published English article with a reconciled source mapping for the
   pilot. Both hosts need the article-path rules above. You may temporarily narrow
   each rule to its pilot article path; a reject-all rule would block full-app
   framing. For example, the paired passkey article uses these pilot rules:

   ```text
   blog.vpsfree.org: \A/two-factor-login-with-passkeys/?\z
   blog.vpsfree.cz:  \A/dvoufaktorove-prihlasovani-s-passkey/?\z
   ```

   On a desktop browser, open `/admin/customize/embedding`, choose
   **Hosts**, and expand **Configuration snippet**. Verify that **Full app mode**
   and the effective server setting are enabled.
   In a separate tab, open the selected final static English article. In the
   browser's developer tools, use **Elements** to add
   `<div id="discourse-comments"></div>` inside that page's `#respond` section.
   In **Console**, run only the JavaScript inside the generated snippet's
   `<script>` element, replacing `EMBED_URL` with the exact shared English
   canonical URL. Retain `discourseUrl: 'https://discourse.vpsfree.cz/'` and
   boolean `fullApp: true`.
   This deliberately loads the [native iframe loader][native-loader] and can
   create a topic and notifications. It changes only that tab's temporary DOM;
   leave source files, served HTML and the blog's `enabled = false` unchanged.
3. Repeat the same steps in a tab on the paired Czech article, using the same
   English `EMBED_URL`. For a concurrent check, prepare one tab per production
   origin and run that same snippet in both. Limit this to the pilot article;
   do not open the archive. Record the single topic URL and verify the extracted
   prose, code, images and links from the static English page. Check anonymous
   reading, native login transition, actual inline reply with ordinary account
   permissions, notifications and both hosts' iframe CSP/referrer behavior. Test
   cross-site cookie restrictions and the top-level forum fallback. Source checks
   do not prove browser authentication, especially from the English host.
   Reloading discards the temporary DOM changes. Keep previews and drafts
   isolated from the production forum.
4. After setup, mappings and the pilot are accepted, restore the normal path
   rules above if the pilot used narrower rules. Prepare a reviewed enablement
   release that updates the affected production assertions in `bin/check`: its
   generic script allowlist and root checks currently require disabled output.
   Make those checks validate the enabled native embed and listing-count script
   while retaining the preview, origin and article-state guards. Run the enabled
   production checks as part of that release, alongside setting `hugo.toml` to:

   ```toml
   [params.discourse]
   enabled = true
   ```

After the opt-in release, check a listing page in each language: the returned
reply labels must refer to the same forum topic and leave the local article links
unchanged.

Keep all existing environment, base-URL, draft and server guards. Future articles
within the source-path namespace need no per-article forum action. Record the
observed version, category, author, settings and pilot results in the operator's
rollout record. Listed-on-first-view behavior would require a separate deliberate
change to both visibility settings after reviewing notification effects.

`nix develop -c bin/check` covers disabled and opt-in rendering using isolated local
content and static outputs. It performs no forum requests. Browser verification
of a local candidate must use synthetic origins and blocked forum requests.
Loading an enabled production embed is not a read-only appearance check.

Check the documented host rules with Ruby from the locked Nixpkgs input:

```sh
nix shell --no-write-lock-file --no-update-lock-file --inputs-from . nixpkgs#ruby -c ruby tools/check-discussion-paths.rb
```

This check makes no forum requests.

## Stop imports or recover

Disable the blog embed through the normal content release. To stop new imports
immediately, the operator can narrow the affected source-host path rule through
the forum UI while keeping the host row needed for framing. Keep direct forum
links and preserve every topic, source mapping, reply and archived comment.

Correcting a host rule affects subsequent host selection; it does not move an
already miscategorized topic. Use the staff topic editor to move the existing
topic to the intended category. Preserve its source mapping, author, replies
and listed/unlisted state. Do not delete or reimport it as a repair.

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
