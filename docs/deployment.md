# Building and delivering a release

The workflow checks and builds both language sites. Trusted protected-main runs
also retain a release artifact. Only protected-main **push** runs upload it to
`https://blog.vpsfree.cz/_deploy/blog`; manual runs prepare artifacts without
authorizing delivery. Feature pushes and pull requests run checks without the
deployment secret.

The separate `deploy` job uses the `blog-production` Actions environment. An
operator must restrict that environment to protected `main`, set its
`BLOG_DEPLOY_KEY` secret, and provision the matching target key. The job has
read-only repository permissions. Its final step succeeds only after the target
confirms that the exact validated release and its receipt are durable and
selected. Builds and uploads do not deploy a system or change backend routing.

This workflow is the publication authority. The target authenticates the
deployment key and validates package consistency. It does not query GitHub
independently to verify current main, branch protection or run success. Source
SHA, run identity and build inputs are authenticated sender assertions. Anyone
holding the key can authorize a conforming site, including its JavaScript.
Protect main, the workflow and the environment accordingly.

## Release identity and retention

`bin/package-release` requires a clean checkout of the exact requested commit
and matching Nix metadata. It emits deterministic `payload.tar.gz` and
`receipt.json`. The archive contains `cs/`, `en/`, `metadata.json` and a
`release.json` envelope; the metadata and envelope remain outside served roots.
They bind the repository, workflow path, source SHA, run ID/attempt, pinned
build inputs and complete file hashes, including Pagefind. The receipt hashes
the archive. Dirty or null source identities remain supported for local
previews but cannot become releases.

Actions retains `blog-<source SHA>` for the requested 90 days, subject to the
repository's retention policy. The deploy job downloads that exact artifact
from its own run. Target retention can prune old release directories and
archives while preserving served and protected recovery releases, publication
records, immutable CSS and current media. The configuration repository's
operations guide defines the retention policy and inspection commands. Keep
separate backups; Actions retention is not the recovery contract. No Hugo build
runs on the VPS.

Rerunning only a failed deploy job reuses the retained artifact and its original
build attempt. The deployment job does not rewrite that identity. Rerunning all
jobs rebuilds and replaces the Actions artifact under the same name; its artifact
ID and bytes may change. Target archives, receipts and ordering remain unchanged
by that replacement.

## Synchronous upload

`bin/upload-release` wraps the two package files in one deterministic ZIP and
sends it with verified HTTPS to the fixed endpoint. It follows no redirects and
has no insecure TLS option. The deployment key is read from the job
environment, not an argument, URL, artifact or log. The client signs the
method, exact path, workflow run number and SHA-256 of the ZIP body. The
configuration repository's
[operations guide](https://github.com/vpsfreecz/vpsfree-cz-configuration/blob/master/docs/operations/blog-static.md)
owns the exact protocol and target contract.

Both nginx hops permit at most 512 MiB only at the exact Czech upload location.
The validator also caps expanded content at 512 MiB and 25,000 files. English,
disabled publication and other reserved deployment paths do not reach the
receiver. The retired webhook namespace returns 404. The provisional endpoint
timeouts are 180 seconds; the client has a 300-second total budget and at most
three attempts. Full-size measurement is required before deployment.

A successful HTTP 200 confirms the source, release key, current receipt digest,
body digest and workflow identity. The client checks every returned identity.
Busy, paused, malformed, stale and conflicting requests return non-2xx
responses. The client retries transient failures using the same ZIP bytes and
signature. A lost reply can follow a successful commit, so an Actions failure
means delivery was not confirmed. Retry the exact package or inspect root
status before deciding whether content changed. No background queue or deferred
publication exists.

The target orders successful uploads by `(GITHUB_RUN_NUMBER,
GITHUB_RUN_ATTEMPT)` within this fixed workflow. It binds each accepted order
to the run ID, source and body digest. Lower orders and conflicting reuse are
rejected. An identical retry succeeds only while that exact upload remains
selected. A higher attempt may advance the durable order even when content is
unchanged. Workflow concurrency prevents cancellation during upload, but the
target ordering check remains necessary. This cannot detect a newer main commit
that has not arrived. Recreating the workflow's ordering namespace needs an
explicit operator reset.

## Maintenance and recovery

Static storage and publication default off. With static storage `enable=true`,
the backend frontend on port 80 forwards both fixed language Hosts to loopback
port 8080; with `enable=false`, both return 503. Missing content while enabled
returns 404. The public proxy still forwards both hosts to backend port 80.
The current configuration has no `serveStatic` selector or WordPress fallback.
After enabling storage and publication, explicitly resume the installed policy
before uploads can select content. Verify the selected release on backend
`127.0.0.1:8080` with each fixed language Host.

Root `blog-static-release maintenance-enter` waits on the same stable lock as
pointer transactions and persists pause. The native pre-switch check requires
pause before system changes, including disabling publication. After deployment
and verification, `maintenance-exit` reconciles receipts and resumes only the
selected policy and system generation. It never replays an upload. A request
already receiving data cannot commit after pause or a system/policy change.

Root `rollback --release KEY --expected-current DIGEST` selects an exact
retained release through an irreversibly unprivileged content child. It
persists pause and preserves the greatest committed upload order. Resume does
not authorize an old request to undo rollback; use a newer authorized upload to
publish again. Unknown pointers, invalid receipts or failed durability barriers
require operator reconciliation. Rollback requires a complete retained release;
pruned payloads are no longer rollback targets. Keep prior systems and separate
backups.

Policy/control schema 2 is the signed-upload authority boundary. Retained
schema-1 release content can be restored through the compatible schema-2
publisher; this does not establish a system rollback to the older schema-1
generation, whose maintenance check rejects schema-2 state. Do not run old
publication writers against the new state.

Normal recovery uses a complete retained static release and the guarded rollback
above. Restoring WordPress requires a retained, compatible historical schema-2
system, its prior inputs and retained site/database data, and that system's
routing selector. Content rollback alone does not restore WordPress. Before
reactivation, verify activation and control-state compatibility and inspect old
MySQL/tmpfiles rules for changes to retained ownership and permissions. Keep
WordPress/database backups and account identities throughout the transition.
Live TLS, runtime credentials, systemd authority and production delivery need
separate operator verification.

## Local checks

```sh
nix develop -c bin/check
nix develop -c bin/check-release
nix build .#site
```

`bin/check-release` uses small offline fixtures for package identity,
deterministic archives, tamper detection, exact-byte lost-reply retries,
response validation and workflow secret/event scoping. Configuration tests
cover upload authentication, ZIP and payload bounds, ordering, crash
reconciliation, maintenance and routing. These checks do not prove live
branch/environment settings or production reachability.

Static-content rollback restores the complete site and search index together.
Pagefind's hashed shards may disappear for an older open tab; the search
adapter reports load failures and offers a reload. Its stable entry files
retain ordinary HTTP caching. The [discussion guide](discussions.md) describes
the separate forum embed and its setup gates. Uploads create no
discussion topics.

Unlisted articles use the same main release path and complete file accounting as
published articles. Build them with templates and checks that support unlisted
content; older templates may expose it in listings. An exact-release rollback
restores its prior complete payload.
