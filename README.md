# Klippster Community — Format Pack registry

The community registry of **Format Packs** for [Klippster](https://github.com/SimplyLiz/Klippster).
Distribution is **Git, not a backend** (the same model as the [Homebrew tap](https://github.com/SimplyLiz/homebrew-klippster)):
each pack is a folder here, and the app fetches a generated [`registry.json`](registry.json) index to
discover, download, and verify packs.

## What's a Format Pack?

A converter Klippster can run — e.g. "PDF → Markdown" or "HTML → Markdown". A pack is a folder
under [`packs/`](packs/) containing a `klippster.json` manifest plus its files (a sandboxed
`convert.wasm` module, or a declarative template). See the
[WASM ABI](https://github.com/SimplyLiz/Klippster/blob/main/docs/format-packs/wasm-abi.md) and the
[`text-uppercase`](packs/com.example.text-uppercase) reference pack.

## Layout

```
packs/
  <pack-id>/                 ← folder name must equal the manifest `id`
    klippster.json             the manifest (schema/klippster-pack.schema.json)
    convert.wasm               the module, for provider: wasm
    README.md                  what the pack does
registry.json                ← generated index the app fetches (do not hand-edit)
schema/
  registry.schema.json         the registry.json schema
  klippster-pack.schema.json   the pack manifest schema
scripts/build_registry.py    ← regenerates + validates registry.json (stdlib only)
```

## registry.json

The index the app consumes. One entry per pack with its `id`, `version`, `provider`,
`inputs`/`outputs`, and — for every file in the pack folder — a **download URL and SHA-256**, so the
client verifies integrity before installing (a tampered download is rejected). It's **generated**;
never edit it by hand:

```sh
python3 scripts/build_registry.py          # regenerate
python3 scripts/build_registry.py --check  # CI: fail if stale or a pack is invalid
```

Output is deterministic (sorted, no timestamps), so `--check` reliably detects drift.

## Signing (issue #16)

`registry.json` carries the SHA-256 of every pack file — but those checksums are only trustworthy if
the index itself is authentic. So the maintainer signs `registry.json` with an offline Ed25519 key and
commits a detached signature, [`registry.json.sig`](registry.json.sig). Klippster **pins the matching
public key** and verifies the signature before trusting anything inside the index. The chain:

```
pinned public key → verified registry.json → trusted per-file SHA-256 → verified pack files
```

The private key is held offline by the maintainer and is never committed (see `.gitignore`) nor stored
in CI. The public key lives at [`keys/registry_signing_pub.pem`](keys/registry_signing_pub.pem). To
(re)sign after any change to the packs tree:

```sh
scripts/sign_registry.sh   # regenerates + signs; needs OpenSSL 3 (brew install openssl@3)
```

`sign_registry.sh` also advances a monotonic **`registrySerial`** (see below), so this signed release
supersedes the previous one. Commit **both** `registry.json` and `registry.json.sig`. CI verifies the
signature on `main`. Rotating the signing key requires a Klippster app release (the public key is
compiled in).

### Anti-rollback (`registrySerial`)

`registry.json` carries a monotonic `registrySerial`. It lives *inside* the signed bytes, so it's
authenticated with the rest of the index, and the app persists the highest serial it has ever trusted
and **refuses any index whose serial is lower** — defeating a replay of an *older, genuinely-signed*
index (e.g. to hide a newer pack) that a stale or hostile host could otherwise serve.

Mechanics that keep this compatible with the deterministic `--check`:

- A plain `build_registry.py` **preserves** the committed serial (floored to 1), so regeneration is
  byte-identical and `--check` still detects drift.
- `build_registry.py --bump` advances it by one. `sign_registry.sh` runs `--bump`, so the serial moves
  forward once per signed release — contributors never touch it (a plain rebuild leaves it unchanged).

Not covered: there's no signed freshness/expiry timestamp, so within the rollback floor the client
can't distinguish a current index from an indefinitely-cached recent one. That's an availability
concern, not code execution — every pack file is still individually SHA-256-verified against the
authenticated index before install.

## Contributing a pack

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: add `packs/<your-id>/`, run the generator, open a
PR. CI validates every manifest and that `registry.json` is up to date. The review + trust policy is
tracked in the main repo (issue #16).

## Installing packs

Through Klippster's in-app **pack browser** (Settings → Plugins), which reads this `registry.json`.
There's no manual install flow — the app downloads, checksum-verifies, and installs.

> **Private for now.** While this repo is private, the app can't fetch it unauthenticated. It'll be
> made public before packs ship to users.
