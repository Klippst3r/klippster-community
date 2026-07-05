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

## Contributing a pack

See [CONTRIBUTING.md](CONTRIBUTING.md). In short: add `packs/<your-id>/`, run the generator, open a
PR. CI validates every manifest and that `registry.json` is up to date. The review + trust policy is
tracked in the main repo (issue #16).

## Installing packs

Through Klippster's in-app **pack browser** (Settings → Plugins), which reads this `registry.json`.
There's no manual install flow — the app downloads, checksum-verifies, and installs.

> **Private for now.** While this repo is private, the app can't fetch it unauthenticated. It'll be
> made public before packs ship to users.
