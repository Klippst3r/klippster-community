# Tech Docs

A code-forward documentation theme — Heros sans-serif body, teal headings and Inconsolata code set in a shaded box. Good for READMEs, technical notes and API-style docs.

Install it, then in Finder right-click a Markdown file → **Convert to → Tech Docs**
(or pick it from the Cmd-Shift-C menu). Klippster writes a styled PDF beside the
source file.

**Requirements.** Like any pandoc theme pack, this needs pandoc **and** a PDF
engine (a LaTeX engine). The easiest to install is Tectonic:
`brew install pandoc tectonic`. With no engine present, the conversion won't run.

**Fonts.** Uses TeX Gyre Heros (sans) and Inconsolata (mono) from the TeX distribution — fetched automatically the first
time you render, nothing to install.

The look lives in `theme.latex`, a standard pandoc LaTeX template
(`$body$`, `$highlighting-macros$`). Fork it to adjust colours, fonts, margins
or headings — see the authoring guide in `docs/user/`.
