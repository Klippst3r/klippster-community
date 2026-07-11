# Optimize SVG — WASM Format Pack

Shrinks SVG files by stripping the cruft that bloats editor exports, while preserving how the image
renders. A pure-Rust WASM converter implementing the [guest ABI v1](../../../docs/format-packs/wasm-abi.md);
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
WasmKit's interpreter (raster-image packs are non-viable — see [docs/optional-tools.md](../../../docs/optional-tools.md)).

## Build

```sh
rustup target add wasm32-unknown-unknown
./build.sh   # → convert.wasm
```
