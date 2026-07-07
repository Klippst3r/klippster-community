# Klippster Community — Format Pack registry

The community registry of **Format Packs** for [Klippster](https://github.com/Klippst3r/Klippster)
(this repo: [`Klippst3r/klippster-community`](https://github.com/Klippst3r/klippster-community)).
Distribution is **Git, not a backend** (the same model as the [Homebrew tap](https://github.com/Klippst3r/homebrew-klippster)):
each pack is a folder here, and the app fetches a generated [`registry.json`](registry.json) index to
discover, download, and verify packs.

## New here? Start with the author guide

If you want to **build a pack**, read the plain-language walkthrough first:
**[`docs/user/authoring-packs.md`](docs/user/authoring-packs.md)** — idea → converter → pull request.
Then copy a ready-made starter from **[`examples/`](examples/)** (one per provider kind). The rest of
this README is the reference: what the repo is, how the index works, and how trust is enforced.

## What's a Format Pack?

A converter Klippster can run — e.g. "PDF → Markdown" or "HTML → Markdown". Once installed, the
conversion appears everywhere Klippster works: the Finder right-click menus (Paste / Copy / Convert)
and the keyboard shortcuts. A pack is a folder under [`packs/`](packs/) containing a `klippster.json`
manifest plus whatever files it ships. See the guest
[WASM ABI](https://github.com/Klippst3r/Klippster/blob/main/docs/format-packs/wasm-abi.md), the
[`text-uppercase`](packs/com.example.text-uppercase) reference pack, and the copy-and-adapt
[`examples/`](examples/).

## Provider kinds — how a pack's conversion runs

Every pack declares one **provider**. Pick this first (details + starters in [`examples/`](examples/)):

| Provider | How it runs | Author ships | Use when |
|----------|-------------|--------------|----------|
| **`wasm`** | Your compiled module, in a strict host sandbox | A `.wasm` module | You want a conversion you own that runs on every machine — **the default for third-party authors** |
| **`host`** | A command-line tool the user installed (e.g. pandoc) | Manifest only | A great CLI tool already does the job |
| **`template`** | A host engine driven by allowlisted options | Manifest only | You want to steer that tool (e.g. pandoc `from`/`to`/`wrap`) without code |
| **`native`** | A converter built into the app | Manifest only | Referencing something the app already ships (maintainer territory) |

**Today only `wasm` executes third-party conversion code.** `host`/`template` depend on machinery the
app wires up, and `native` is app-provided — so for a converter you author end-to-end, use `wasm`.

## Guest ABI v1 (for `wasm` packs)

A `wasm` converter is a `wasm32` module that **imports nothing** and exports exactly four things:
`memory`, `buffer_ptr() -> i32` (offset of a shared byte buffer), `buffer_cap() -> i32` (its
capacity), and `convert(input_len) -> i32` (the conversion). The host writes `input_len` bytes into
the buffer, calls `convert`, and reads back the returned length; a **negative** return signals an
error. The entry point name is overridable via the manifest's `options.entrypoint` (**the only
allowed wasm option**, defaulting to `convert`). No permissions are granted, and any declared
`permissions` entry is refused. The runtime enforces input/output/memory ceilings and a wall-clock
timeout. Full contract:
[**WASM ABI v1**](https://github.com/Klippst3r/Klippster/blob/main/docs/format-packs/wasm-abi.md).

## Layout

```
packs/
  <pack-id>/                 ← folder name must equal the manifest `id`
    klippster.json             the manifest (schema/klippster-pack.schema.json)
    convert.wasm               the module, for provider: wasm
    README.md                  what the pack does
examples/                    ← copy-and-adapt starters, one per provider kind
  <kind>/                      OUTSIDE packs/ on purpose — never scanned into registry.json
docs/user/                   ← plain-language author walkthrough
registry.json                ← generated index the app fetches (do not hand-edit)
registry.json.sig            ← detached Ed25519 signature over registry.json (maintainer)
schema/
  registry.schema.json         the registry.json schema
  klippster-pack.schema.json   the pack manifest schema
scripts/build_registry.py    ← regenerates + validates registry.json (stdlib only)
```

Only [`packs/`](packs/) is scanned into `registry.json`. [`examples/`](examples/) and
[`docs/`](docs/) are author material and never become installable content.

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

Read the walkthrough first — [`docs/user/authoring-packs.md`](docs/user/authoring-packs.md) — and
copy a starter from [`examples/`](examples/). The mechanical steps are in
[CONTRIBUTING.md](CONTRIBUTING.md): add `packs/<your-id>/` (folder name **must** equal the manifest
`id`), run the generator, commit your pack **and** the regenerated `registry.json`, and open a PR. CI
validates every manifest against the schema and that `registry.json` is up to date; a maintainer then
reviews the pack ([REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)) and signs the release. You never sign
and never touch `registrySerial`.

## Installing packs

Through Klippster's in-app **pack browser** (Settings → Plugins), which reads this `registry.json`.
There's no manual install flow — the app downloads, checksum-verifies, and installs.

> **Private for now.** While this repo is private, the app can't fetch it unauthenticated. It'll be
> made public before packs ship to users.
