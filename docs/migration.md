# Importing the captured WordPress archive

The importer reads a private local MariaDB restore and the captured uploads
archive. It writes public Czech Hugo bundles, shared author/taxonomy metadata,
approved historical comments, legacy upload files and an import manifest.
Neither the generated site nor its Nix build needs WordPress, PHP or a database.

Keep the original SQL, private key state and raw post bodies in owner-only
operator storage outside this clone, session scratch directories and build
inputs. Verify the recovery receipt's SQL/archive checksums before restoring.
The captured database snapshot is internally consistent; matching upload
metadata before/after capture does not establish an atomic database/filesystem
cutover snapshot. A production transition requires separate approval. Before
switching, briefly check for new or changed articles or comments and refresh the
capture only if needed; no writer freeze is planned. This importer never connects
to production.

## Restore and project locally

Use MariaDB 11.4.12, matching the captured database. Initialize a disposable data
directory with `mariadb-install-db`, then run `mariadbd --skip-networking` with a
Unix socket inside an owner-only parent directory. Disable event scheduling,
general/slow query logs and binary logging. Set `secure-file-priv` to a private
empty directory; MariaDB treats the string `NULL` as a path. Register the local
server with the host's temporary-service launcher in a managed environment.
Do not point these commands at an existing application database or reuse its
socket. Restore the SQL with the supported MariaDB client and keep all restore
output private. Restoring private SQL is preparation, not publication.

Obtain the matching WordPress 7.1.2 `wp-includes/formatting.php` from a trusted
package. Its required SHA-256 is
`350f6b32303915df970bb0e3ea360fcd54bb0b8a7ecc3d504c3d860ab9468d32`.
The adapter verifies the hash and includes only this library, calling
`convert_chars` and `wpautop`. It never loads `wp-load.php`, configuration,
plugins or themes. PHP is needed only for this migration command.

Supply local paths explicitly; the following names are placeholders:

```sh
python3 tools/import-wordpress \
  --client /path/to/mariadb --db-user local-restore-owner \
  --socket /private/operator-storage/database.sock \
  --uploads-archive /private/operator-storage/wordpress-state.tar.gz \
  --formatting /trusted/wordpress/wp-includes/formatting.php \
  --output /private/operator-storage/projected-public
```

Use `--ids 615,37,662` to check the representative code, media and threaded-comment
articles before generating the complete corpus. The full command expects this
captured corpus: 125 published password-free articles, six authors, 107 approved
comments with 43 replies, 144 attachment records and 569 upload files totaling
50,375,369 bytes. It queries explicit public fields using native database JSON
output, never a custom SQL parser. Account credentials, email/address fields,
spam, revisions and unrestricted options/metadata are not selected.

The output contains native Czech HTML bundles at the paths recorded for each
immutable article ID in `data/migration/source-manifest.json`. The importer uses
this existing map for fresh output and in-place reruns; `--source-manifest`
selects a reviewed fixture map. Unknown IDs or invalid/duplicate paths refuse
before writing. Assign a path explicitly before importing a new ID; titles never
relocate an existing bundle. Original raw body hashes and complete generated
file hashes are
different inputs: `params.source_body_sha256` identifies private raw source;
`data/migration/source-manifest.json` also records `cs_file_sha256`, which English
drafts use for source freshness. The manifest includes source word counts,
conversion exceptions, original Czech GUIDs via shared article metadata, asset
digests and legacy archive/query alias evidence. Alias records describe required
compatibility; they do not configure a server or prove deployed redirects.

Raw article bodies stay private. Public HTML preserves visible text, code,
native `<!--more-->` boundaries and `more-<id>` anchors. A fixed allowlist strips
active content and unsafe attributes/URLs. Article video iframes accept only
YouTube/SuperLectures over HTTPS; comments never accept iframes. Historical
comment names are plain display fields, and comment HTML is sanitized separately.
Theme templates own thread rendering and `comment-<id>` anchors. They must escape
plain names and use trusted HTML rendering only for the sanitized body fields.

`wptexturize` is deliberately not approximated: its localized WordPress hooks
are unavailable to this pure-library adapter. The manifest marks that difference
for every article. Review typography against representative original pages;
visible-text equality alone does not certify exact browser rendering. Unsupported
tags/attributes or embeds are reported as concrete conversion exceptions rather
than silently disappearing. No shortcode subsystem is used.

## Validate and reconcile

```sh
nix develop -c python3 tools/import-wordpress-check --source /path/to/projected-public
```

The check verifies all generated hashes, counts, public field shapes, comment
parents/cycles, safe HTML boundaries, article identities and legacy upload
references. An optional `--private-posts` points to a private allowlisted source
JSON for full visible-text comparisons; never add that file to the clone. Run
the import twice into separate fresh output directories and compare every
managed file byte-for-byte before accepting a new projection. Confirm each
media file digest, not just its filename or total size.

After inspecting the fresh output, run the importer again with the clone as
`--output`. It writes only its explicit generated-file set: Czech bundles,
public data and `static/wp-content/uploads/`. It never cleans the content tree,
touches English variants, `content/_content.gotmpl` or theme assets. The previous
manifest binds managed files; a changed existing file without its matching prior
hash causes refusal, preserving manual corrections. Resolve such conflicts
explicitly rather than deleting the prior manifest or forcing an overwrite.

Use the normal site checks and theme/browser review after integration of the
public projection. Feed serialization, author/category/tag/date archives and
legacy query routing belong to their owning templates/hosting configuration.
A source import, successful build or feature-branch push does not change the
live WordPress service or authorize a production transition.
