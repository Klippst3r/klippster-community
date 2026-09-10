# Academic

A classic academic article theme — Times-style serif, numbered sections, indented justified paragraphs and restrained links. Good for essays, papers and long-form writing.

Install it, then in Finder right-click a Markdown file → **Convert to → Academic**
(or pick it from the Cmd-Shift-C menu). Klippster writes a styled PDF beside the
source file.

**Requirements.** Like any pandoc theme pack, this needs pandoc **and** a PDF
engine (a LaTeX engine). The easiest to install is Tectonic:
`brew install pandoc tectonic`. With no engine present, the conversion won't run.

**Fonts.** Uses TeX Gyre Termes (serif) from the TeX distribution — fetched automatically the first
time you render, nothing to install.

The look lives in `theme.latex`, a standard pandoc LaTeX template
(`$body$`, `$highlighting-macros$`). Fork it to adjust colours, fonts, margins
or headings — see the authoring guide in `docs/user/`.
