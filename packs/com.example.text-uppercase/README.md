# Uppercase Text — example WASM converter pack

A minimal, working Klippster **Format Pack** that converts text → text by uppercasing ASCII. Copy
this folder to start your own converter. Full contract: [`docs/format-packs/wasm-abi.md`](../../../docs/format-packs/wasm-abi.md).

## Layout

```
text-uppercase/
  klippster.json   ← the manifest Klippster reads (id, types, provider: wasm, module)
  convert.wasm     ← the compiled module (committed so the pack works without a build step)
  src/lib.rs       ← the guest source
  build.sh         ← rebuilds convert.wasm from src/lib.rs
```

## The manifest

```json
{
  "id": "com.example.text-uppercase",
  "name": "Uppercase Text",
  "version": "1.0.0",
  "inputs": ["txt"],
  "outputs": ["txt"],
  "provider": "wasm",
  "module": "convert.wasm"
}
```

`inputs`/`outputs` are content-type spellings (extension, MIME, UTI, or alias). `provider: "wasm"`
tells Klippster to run `module` in its sandboxed runtime. Do **not** set `permissions` — the runtime
grants none, and any declared permission is refused (see the ABI doc).

## The guest (ABI v1)

`src/lib.rs` exports exactly four things:

- `memory`
- `buffer_ptr() -> i32` — where in memory the host reads/writes bytes
- `buffer_cap() -> i32` — how many bytes fit there
- `convert(input_len: i32) -> i32` — the conversion. The host has written `input_len` bytes at
  `buffer_ptr()`; write your result back to the same buffer and return its length, or a negative
  value to signal an error.

The module is fully sandboxed: no filesystem, no network, no clock — only the bytes the host hands in.

## Build

```sh
rustup target add wasm32-unknown-unknown   # once
./build.sh                                 # → convert.wasm
```

You can write the guest in any language that targets `wasm32` and can export these functions
(Rust, C, Zig, AssemblyScript…). Rust is shown here.
