#!/usr/bin/env python3
"""Render a template PDF-theme pack's canonical sample document to a PNG preview.

    render_preview.py <pack-dir> <out.png> [--sample sample.md]

Runs the *same* pandoc invocation the app's TemplateExecutor uses
(`--template <theme> --pdf-engine=<engine> --standalone`), then rasterises the
first page with poppler's `pdftoppm`. Requires pandoc, a PDF engine
(tectonic/xelatex/typst/…), and poppler-utils. Used by CI and runnable locally.

Exit non-zero (with pandoc's stderr) if the theme doesn't compile — so this
doubles as pack validation.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SAMPLE = os.path.join(REPO, "previews", "sample.md")
# Cap how many pages a preview stacks, so a runaway document can't produce a giant image.
MAX_PREVIEW_PAGES = 6
# Preference order matches the app's PDFEngine ordering (tectonic first: self-contained).
ENGINE_PREFERENCE = ["tectonic", "xelatex", "lualatex", "typst", "pdflatex", "weasyprint", "wkhtmltopdf"]


def find_engine(name):
    for candidate in ([name] if name else ENGINE_PREFERENCE):
        if candidate and shutil.which(candidate):
            return shutil.which(candidate)
    return None


def die(message):
    sys.stderr.write(message.rstrip() + "\n")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pack_dir")
    parser.add_argument("out_png")
    parser.add_argument("--sample", help="override the sample markdown")
    args = parser.parse_args()

    manifest_path = os.path.join(args.pack_dir, "klippster.json")
    if not os.path.isfile(manifest_path):
        die(f"no klippster.json in {args.pack_dir}")
    manifest = json.load(open(manifest_path))

    if manifest.get("provider") != "template":
        die(f"not a template pack (provider={manifest.get('provider')!r})")
    if "pdf" not in (manifest.get("outputs") or []):
        die("pack does not output pdf")

    options = manifest.get("options") or {}
    template = options.get("template")
    if not template:
        die("template pack has no options.template")
    template_path = os.path.join(args.pack_dir, template)
    if not os.path.isfile(template_path):
        die(f"template file missing: {template}")

    engine = find_engine(options.get("pdf-engine"))
    if not engine:
        die("no PDF engine installed (e.g. `brew install tectonic`)")
    pandoc = shutil.which("pandoc")
    if not pandoc:
        die("pandoc not installed")
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        die("pdftoppm (poppler) not installed")

    # Sample: explicit --sample, else the pack's own sample.md, else the canonical one.
    pack_sample = os.path.join(args.pack_dir, "sample.md")
    sample = args.sample or (pack_sample if os.path.isfile(pack_sample) else DEFAULT_SAMPLE)
    from_format = options.get("from") or "gfm"

    with tempfile.TemporaryDirectory() as tmp:
        pdf = os.path.join(tmp, "out.pdf")
        result = subprocess.run(
            [pandoc, "--from", from_format, "--template", template_path,
             f"--pdf-engine={engine}", "--standalone", "-o", pdf, sample],
            capture_output=True, text=True, timeout=180)
        if result.returncode != 0 or not os.path.isfile(pdf):
            die(f"pandoc failed rendering the theme:\n{result.stderr}")

        base = os.path.join(tmp, "page")
        # No -f/-l: rasterise every page, so a multi-page document previews in full.
        rasterise = subprocess.run(
            [pdftoppm, "-png", "-r", "150", pdf, base],
            capture_output=True, text=True, timeout=120)
        if rasterise.returncode != 0:
            die(f"pdftoppm failed:\n{rasterise.stderr}")

        pngs = sorted(
            (f for f in os.listdir(tmp) if re.fullmatch(r"page-\d+\.png", f)),
            key=lambda n: int(re.search(r"(\d+)", n).group(1)))
        if not pngs:
            die("no PNG produced")
        pages = [os.path.join(tmp, p) for p in pngs[:MAX_PREVIEW_PAGES]]

        out_dir = os.path.dirname(os.path.abspath(args.out_png))
        os.makedirs(out_dir, exist_ok=True)
        stack_pages(pages, args.out_png)

    extra = "" if len(pngs) <= MAX_PREVIEW_PAGES else f" (first {MAX_PREVIEW_PAGES} of {len(pngs)} pages)"
    print(f"wrote {args.out_png}{extra}")


def stack_pages(pages, out_png):
    """Stack page PNGs vertically into one image with a light-grey gap between pages, so a
    multi-page preview reads as a single scrollable thumbnail. A single page is copied as-is."""
    if len(pages) == 1:
        shutil.copyfile(pages[0], out_png)
        return
    from PIL import Image
    gap = 24
    gap_colour = (208, 210, 214)
    imgs = [Image.open(p).convert("RGB") for p in pages]
    width = max(im.width for im in imgs)
    height = sum(im.height for im in imgs) + gap * (len(imgs) - 1)
    canvas = Image.new("RGB", (width, height), gap_colour)
    y = 0
    for im in imgs:
        canvas.paste(im, ((width - im.width) // 2, y))
        y += im.height + gap
    canvas.save(out_png)


if __name__ == "__main__":
    main()
