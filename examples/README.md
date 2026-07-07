# Format Pack examples

Copy-and-adapt starters, one per **provider kind**. These are learning material — they live
**outside** [`packs/`](../packs/), so they are never scanned by `scripts/build_registry.py` and never
become registry entries. When you're ready to publish, copy a starter into `packs/<your-id>/`, rename
the folder to your pack `id`, and follow [CONTRIBUTING.md](../CONTRIBUTING.md).

| Folder | Provider | What it shows | Ships code? |
|--------|----------|---------------|-------------|
| [`com.example.uppercase-text`](com.example.uppercase-text/) | `wasm` | A full build-it-yourself sandboxed converter — manifest, Rust source, build script | Yes (`.wasm` you build) |
| [`com.example.html-to-markdown`](com.example.html-to-markdown/) | `host` | Delegating to a user-installed binary (pandoc) | No |
| [`com.example.html-to-gfm`](com.example.html-to-gfm/) | `template` | A declarative pack that drives a host engine with allowlisted options | No |
| [`com.example.pdf-to-markdown`](com.example.pdf-to-markdown/) | `native` | Re-declaring a converter the app already ships | No |

## Which provider should I pick?

- **`wasm`** — you want to ship your own conversion logic that runs on any user's machine with no
  extra installs. This is the one third parties can fully own: your compiled module runs in
  Klippster's sandbox. **If in doubt, this is the answer.**
- **`host`** — the conversion is already done well by a command-line tool the user installs
  themselves (e.g. pandoc). Your pack is metadata that points at that binary. The tool must be
  present on the user's machine or the conversion fails.
- **`template`** — like `host`, but you also supply a small set of allowlisted options that steer a
  host engine (e.g. pandoc's `from`/`to`/`wrap`). No code, no arbitrary flags.
- **`native`** — declares a converter the app already has built in. Only the Klippster maintainers
  can add these meaningfully; it's here so you recognise the kind when you see it.

> **Today only `wasm` executes third-party conversion code.** `host`/`template`/`native` are real
> manifest shapes the app understands, but `host` and `template` depend on machinery the app wires up
> and `native` is app-provided. For a converter you author and control end-to-end, use `wasm`.

Full contract for `wasm`: the **guest ABI v1** —
[`docs/format-packs/wasm-abi.md`](https://github.com/Klippst3r/Klippster/blob/main/docs/format-packs/wasm-abi.md)
in the app repo. Plain-language walkthrough: [`docs/user/authoring-packs.md`](../docs/user/authoring-packs.md).
