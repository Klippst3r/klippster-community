# Security & trust policy

This registry distributes **code that runs on users' machines**. Even a sandboxed converter can waste
resources or emit garbage, and a compromised index could point the app at malicious downloads. This
document is the trust model the registry and the Klippster app enforce, and the policy maintainers
apply when accepting packs (issue #16).

## Threat model

What we defend against:

- **A tampered or forged index.** `registry.json` carries the SHA-256 of every pack file, so if the
  index is trusted, each file is verifiable. The index itself is therefore the thing that must be
  authentic — see *Trust chain*.
- **A tampered pack download.** Every file is checked against its `registry.json` SHA-256 before it
  lands; a single mismatch rejects the whole pack.
- **A rolled-back index.** An older, still-validly-signed index replayed by a stale or hostile host
  (e.g. to hide a newer, fixed pack) is refused via the monotonic `registrySerial`.
- **Resource abuse by a pack at runtime.** Bounded by the app's execution guards (see below).

What we do **not** currently claim to defend against, and rely on human review for:

- A pack whose WASM is functionally malicious *within* the sandbox (produces wrong/garbage output,
  or deliberately hits the resource ceilings). The sandbox contains it; review is what keeps it out.
- Supply-chain compromise of a contributor's own toolchain before they submit.

## Trust chain

```
pinned Ed25519 public key  →  verified registry.json  →  trusted per-file SHA-256  →  verified pack files
   (compiled into the app)      (signature checked          (only trusted once the        (each file hashed
                                 before the index is         index is authentic)            before install)
                                 even decoded)
```

- **Signing is offline.** The maintainer signs `registry.json` with an Ed25519 private key that never
  leaves their machine and is never committed or uploaded to CI. The detached signature is
  [`registry.json.sig`](registry.json.sig); the public half is
  [`keys/registry_signing_pub.pem`](keys/registry_signing_pub.pem), and its raw 32 bytes are **pinned
  in the Klippster app**. See the [README](README.md#signing-issue-16).
- **The app verifies before it trusts.** Klippster checks the signature against its pinned key *before
  decoding* the index, so no attacker-chosen checksum is ever read from an unauthenticated file. An
  unsigned or unverifiable index is refused, identically to a tampered one.
- **Rotating the key needs an app release** — the public key is compiled in. Losing the private key is
  the same: it forces a new key, a new app build, and re-signing the registry.

## Runtime sandbox (what bounds a pack once installed)

- Packs execute **only in the main app process**, never in the sandboxed Finder extension (the
  extension reads manifest metadata for its menus and never runs a converter).
- WASM runs on a pure-Swift interpreter with **no host imports** — no filesystem, no network, no
  process spawning, no clock beyond the guest ABI. A pack can transform its input bytes and nothing
  else.
- **Resource guards** bound every run: input/output/memory ceilings and a wall-clock timeout on a
  dedicated thread. A pack that exceeds them is killed and the conversion fails cleanly.
- **No permissions are granted.** A `wasm` pack must declare no `permissions`; a `template` pack may
  use only allowlisted options. A pack requesting anything else is rejected at review.

## Reporting a problem

- **A malicious or misbehaving pack in the registry:** open a private security advisory on the main
  [Klippster repo](https://github.com/Klippst3r/Klippster/security/advisories) (preferred), or email
  the maintainer. Do not open a public issue for an active abuse report.
- **A signing/verification or index-integrity bug:** same channel — treat it as a vulnerability, not a
  normal issue.

We will pull an offending pack from the registry (removing its entry and re-signing) as the immediate
mitigation; installed copies are removed by the user from the app's Packs pane.

## Status

The registry is **curated** — every pack is reviewed and the index is signed by the maintainer. See
[`REVIEW_CHECKLIST.md`](REVIEW_CHECKLIST.md) for what that review covers. Until the registry goes
public, only maintainer-authored packs ship; external submissions are reviewed under the same
checklist when it opens.
