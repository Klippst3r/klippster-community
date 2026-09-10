# Clean Report

A clean, professional report theme — Palatino serif body, blue sans-serif headings, subtle shaded code blocks, and a footer rule with page numbers. Good for reports, memos and notes.

Install it, then in Finder right-click a Markdown file → **Convert to → Clean Report**
(or pick it from the Cmd-Shift-C menu). Klippster writes a styled PDF beside the
source file.

**Requirements.** Like any pandoc theme pack, this needs pandoc **and** a PDF
engine (a LaTeX engine). The easiest to install is Tectonic:
`brew install pandoc tectonic`. With no engine present, the conversion won't run.

**Fonts.** Uses TeX Gyre Pagella (serif) and TeX Gyre Heros (sans) from the TeX distribution — fetched automatically the first
time you render, nothing to install.

The look lives in `theme.latex`, a standard pandoc LaTeX template
(`$body$`, `$highlighting-macros$`). Fork it to adjust colours, fonts, margins
or headings — see the authoring guide in `docs/user/`.
