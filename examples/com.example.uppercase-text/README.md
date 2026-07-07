# Uppercase Text — `wasm` starter (build it yourself)

A minimal, working Klippster **Format Pack** that converts text → text by uppercasing ASCII. This is
the starter to copy when you want to ship your own conversion logic. Full contract: the guest
[**ABI v1**](https://github.com/Klippst3r/Klippster/blob/main/docs/format-packs/wasm-abi.md).

## What's here

```
com.example.uppercase-text/
  klippster.json   ← the manifest Klippster reads (id, types, provider: wasm, module)
  src/lib.rs       ← the guest source (Rust, no_std)
  build.sh         ← rebuilds convert.wasm from src/lib.rs
  README.md        ← this file
```

There is **no `convert.wasm` committed here** — this is a build-it-yourself starter. Run `build.sh`
to produce it (see below). The published reference pack in
[`packs/com.example.text-uppercase`](../../packs/com.example.text-uppercase) is the payload-only copy
(manifest + compiled module, no source).

## The manifest

```json
{
  "id": "com.example.uppercase-text",
  "name": "Uppercase Text",
  "version": "1.0.0",
  "inputs": ["txt"],
  "outputs": ["txt"],
  "provider": "wasm",
  "module": "convert.wasm",
  "options": { "entrypoint": "convert" }
}
```

- `inputs`/`outputs` are content-type spellings — an extension (`txt`), a MIME type (`text/plain`),
  a UTI (`public.plain-text`), or a known alias. They all resolve to the same canonical type.
- `provider: "wasm"` tells Klippster to run `module` in its sandboxed runtime.
- `module` must be a **bare filename** inside this folder (no `/`, no `..`).
- `options.entrypoint` is **optional** and the **only** allowed option for a wasm pack. It names the
  guest function the host calls; it **defaults to `convert`**, so you can omit it entirely if (like
  here) your export is called `convert`. Set it only if you renamed the export.
- Do **not** set `permissions` — the runtime grants none, and any declared permission is refused.

## The guest (ABI v1)

`src/lib.rs` exports exactly four things and imports **nothing**:

- `memory`
- `buffer_ptr() -> i32` — where in memory the host reads/writes bytes
- `buffer_cap() -> i32` — how many bytes fit there
- `convert(input_len: i32) -> i32` — the conversion. The host has written `input_len` bytes at
  `buffer_ptr()`; write your result back to the same buffer and return its length, or a **negative**
  value to signal an error.

A fresh instance runs each conversion, so memory starts clean every time — don't rely on state
persisting between calls. The module is fully sandboxed: no filesystem, no network, no clock — only
the bytes the host hands in.

## Build

```sh
rustup target add wasm32-unknown-unknown   # once
./build.sh                                 # → convert.wasm
```

You can write the guest in any language that targets `wasm32` and can export these four functions
(Rust, C, Zig, AssemblyScript…). Rust is shown here.

## Test it in Klippster

Because the registry is curated and you haven't submitted yet, stage the pack by hand into the app's
group container to try it end-to-end:

```sh
mkdir -p "$HOME/Library/Group Containers/group.com.macfeatures.klippster/packs/com.example.uppercase-text"
cp klippster.json convert.wasm \
  "$HOME/Library/Group Containers/group.com.macfeatures.klippster/packs/com.example.uppercase-text/"
```

Then reinstall/relaunch Klippster, copy some lowercase text, and use **Paste Clipboard as** — your
converter should appear as an output option.

## Publish it

Copy this folder into `packs/`, rename it so the **folder name equals the manifest `id`**, include
the built `convert.wasm`, regenerate the index, and open a PR:

```sh
python3 scripts/build_registry.py     # from the repo root
```

See [CONTRIBUTING.md](../../CONTRIBUTING.md).
