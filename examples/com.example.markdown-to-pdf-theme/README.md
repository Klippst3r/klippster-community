# Blue Report Theme — `template` PDF starter

A **template-provider** pack that renders **Markdown → PDF**. Like the other template starter it
ships **no converter code** and drives a host engine (pandoc) — but here the point is a **PDF theme**:
the manifest names a LaTeX template that ships alongside it, and pandoc typesets your Markdown through
that template. Styling is unlimited because you own the whole LaTeX document.

```json
{
  "id": "com.example.markdown-to-pdf-theme",
  "name": "Blue Report Theme",
  "version": "1.0.0",
  "provider": "template",
  "engine": "pandoc",
  "inputs": ["markdown"],
  "outputs": ["pdf"],
  "options": { "template": "theme.latex", "from": "gfm" }
}
```

- `provider: "template"` with `outputs: ["pdf"]` — a declarative pack that renders to PDF through the
  host `engine`.
- `engine: "pandoc"` — pandoc does the Markdown parsing and calls the PDF engine.
- `options.template: "theme.latex"` — names the template file **shipped in this folder**. It must be a
  bare filename (no slashes, no leading `..`); Klippster resolves it inside the pack directory.
- `options.from: "gfm"` — tells pandoc to read the input as GitHub-flavoured Markdown.

## What it does

Copy some Markdown, pick this pack, and you get a LaTeX-typeset PDF: blue section and subsection
headings, coloured links, one-inch margins, and block spacing instead of first-line indents.

## The template

`theme.latex` is a **standard pandoc LaTeX template** — an ordinary LaTeX document with a few pandoc
variables that get filled in at render time:

- `$body$` — where your converted Markdown content is inserted. Required; without it the PDF is empty.
- `$highlighting-macros$` — pandoc drops the colour definitions for fenced code blocks here. Include
  it if your input has code blocks, or they won't be styled.
- `\tightlist` — pandoc emits this command around tight lists, so the template defines it (the
  `\providecommand` line) to avoid an "undefined control sequence" error.

Everything else is plain LaTeX you control: colours, fonts, margins, heading formats, headers and
footers. That's the "unlimited styling" — anything your PDF engine's LaTeX can express.

## Requirements

This pack needs **pandoc** and a **PDF engine** installed on the user's machine. pandoc doesn't make
PDFs on its own — it hands the LaTeX to an engine. The simplest to install is Tectonic, a
self-contained LaTeX engine:

```sh
brew install pandoc tectonic
```

Any LaTeX or Typst engine pandoc supports works too (for example a full TeX Live install). If neither
pandoc nor an engine is present, the conversion fails — be upfront about that in your own pack's
README.

## Install and use it

The registry is private while it's being staged, so copy this folder into Klippster's shared pack
directory by hand:

```sh
mkdir -p ~/Library/Group\ Containers/group.com.macfeatures.klippster/packs/com.example.markdown-to-pdf-theme
cp klippster.json theme.latex ~/Library/Group\ Containers/group.com.macfeatures.klippster/packs/com.example.markdown-to-pdf-theme/
```

Reinstall and relaunch Klippster. Then in Finder, right-click a Markdown file and use **Convert to →
Blue Report Theme**, or copy Markdown and pick the theme from the paste menu. The output is a PDF next
to your source (or on the clipboard, depending on the surface).

## Honest expectations

- **The engine must be installed.** No pandoc or no PDF engine means no conversion.
- **You steer and you style, you don't code.** The transform is fixed by the manifest and the
  template; you can't inject arbitrary command-line flags.
- **Wiring is app-side.** Which engines exist and which option keys are honoured is decided by
  Klippster. Model your manifest on this shape and confirm current template support in the app's docs.

For a conversion you fully own end-to-end with no host dependency, use the
[`wasm` starter](../com.example.uppercase-text/).
