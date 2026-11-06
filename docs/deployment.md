# Building a release artifact

The Actions workflow checks the pinned Hugo build and prepares release artifacts
for trusted `main` pushes or manual runs on `main`. Pull requests and other
branches run checks without producing an eligible release. This source workflow
does not deploy the blog. The static hosting candidate and its pull timer remain
disabled; activation is blocked until installed machine-coordination admission
has been implemented and verified.

The workflow uses read-only repository permissions and no deployment credentials.
Its action commit pins were checked against upstream tags: checkout v7.0.1,
install-nix-action v31.11.3 and upload-artifact v7.0.2. Those are reproducible tool
pins, not minimum versions for article authors. `main` protection and a reviewed
workflow are prerequisites for target-side artifact eligibility.

## Release identity

`bin/package-release` accepts only a clean checkout of the exact requested commit
and matching Nix build metadata. Dirty or null identities remain valid for local
authoring/preview, but cannot become release artifacts. The Nix build records its
source and pinned build inputs plus SHA-256 hashes for every served file.

The packager emits deterministic `payload.tar.gz` and `receipt.json` files. The
archive contains separate `cs/` and `en/` document roots, `metadata.json` and a
`release.json` envelope. The envelope/receipt identify `vpsfreecz/blog`, the exact
source SHA, workflow path/run/attempt, artifact name and build inputs. The receipt
also hashes the exact archive; self-referential archive hashes are avoided.
Metadata and receipts are outside the served document roots. Production builds
exclude drafts; the normal human translation-review requirements still apply.

An Actions artifact is named `blog-<source SHA>`. The workflow requests 90 days of
retention; repository/organization retention policy must permit that setting
before enabling the release pipeline. Artifact retention is not a durable backup.
Rare posting does not remove a release already retained by the target.

## Target validation and expiry

The configuration-owned helper independently checks the protected `main` SHA,
verified workflow ID/path, repository, event, successful run and artifact through
the GitHub API. Downloaded identity strings alone are not evidence. It verifies
the archive digest, safe regular-file paths, exact declared payload and every
file hash before staging. It never executes downloaded content. GitHub credentials
are not forwarded to signed artifact-storage URLs or recorded in receipts.

The helper retains exact archives, extracted releases and receipts locally,
including current/previous releases, without automatic garbage collection. If
the artifact for the current authorized SHA is missing or expired, it reports
that SHA and keeps the current site unchanged. It never chooses an older build.
An authorized operator reruns/dispatches the trusted workflow for the same SHA;
the read-only target credential cannot dispatch it. No build runs on the VPS.
A recovered machine needs the retained archive/receipt backup or that exact-source
rebuild, plus the validated WordPress recovery material required before transition.

Source/fixture preparation is separate from enabling this path. Outstanding
operator facts include artifact visibility/read credentials, verified workflow
ID, outbound API/download access, branch protection, retained backup and installed
machine admission. No production credential is provisioned by these changes.

## Checks and transition boundary

```sh
nix develop -c bin/check
nix develop -c bin/check-release
nix build .#site
```

`bin/check-release` uses tiny local Git/site fixtures to check clean identity,
dirty/null rejection, undeclared payload and deterministic packaging. The
configuration repository owns mocked acquisition/transaction checks and its
default-off hosting module. These checks do not prove deployed admission,
credentials, branch policy or network reachability.

The candidate static listener is IPv4 port 8080 behind the existing exact proxy
boundary; WordPress port 80 remains intact. A later approved transition must
address English DNS/TLS, proxy routing, legacy query aliases, feed behavior and
forum setup. Briefly check for new/changed articles or comments before switching
and refresh the capture only if needed; no writer freeze is planned.

The production activation/rollback/pull CLI currently refuses with
`machine-admission-unavailable`. No flag, environment variable or filesystem
lock substitutes for machine ownership. A future admitted transaction must
recheck the authorized head and prior receipt immediately before atomically
switching `current`, reconcile interruptions, retain immutable cached assets and
record rollback separately. Source commits, successful CI or a Git push do not
authorize a production transition.

The [discussion guide](discussions.md) covers the separate default-off embed
source and its runtime setup gates. Neither workflow preparation nor forum
source code changes the current blog or creates discussion topics.
