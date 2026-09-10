# Optimize SVG — WASM Format Pack

Shrinks SVG files by stripping the cruft that bloats editor exports, while preserving how the image
renders. A pure-Rust WASM converter implementing the guest ABI v1 (see [Building a Format Pack](../../docs/user/authoring-packs.md));
imports nothing, fully sandboxed.

**Removes:** XML declaration, DOCTYPE, processing instructions, comments, `<metadata>` subtrees,
Inkscape/Sodipodi editor elements, editor/RDF namespace declarations (`dc`, `cc`, `rdf`, `inkscape`,
`sodipodi`, `sketch`) and their prefixed attributes, and whitespace-only text between elements.

**Preserves:** everything else verbatim — geometry, `<defs>`, gradients, `<style>`/CDATA, `<text>`,
`xmlns`/`xmlns:xlink`. It deliberately does **not** rewrite path data or restructure the document, so
it can't change rendering. (A typical Inkscape export shrinks 60–75%.)

## Why not a full SVGO port?

SVGO ports (e.g. `oxvg`) pull `getrandom`, which can't target `wasm32-unknown-unknown` without a host
import — forbidden by the pack sandbox. And unlike raster codecs, SVG is text, so it runs fast in
WasmKit's interpreter (raster-image packs are non-viable — see [docs/optional-tools.md](https://github.com/Klippst3r/Klippster/blob/develop/docs/optional-tools.md) in the app repo).

## Source and build

This folder ships only the compiled module. The Rust source, `Cargo.toml` and `build.sh` live in
the app repo at [`Packs/examples/svg-optimize`](https://github.com/Klippst3r/Klippster/tree/develop/Packs/examples/svg-optimize);
the committed `convert.wasm` is byte-identical to the one built there.

```sh
rustup target add wasm32-unknown-unknown
./build.sh   # in Packs/examples/svg-optimize → convert.wasm
```
