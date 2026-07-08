#!/usr/bin/env bash
#
# Render preview thumbnails for every PDF theme pack under packs/, into
# previews/<id>/sample.png. Run this before signing (sign_registry.sh calls it)
# so the thumbnails ship inside the signed registry.json — build_registry.py
# adds each pack's `preview` URL when its PNG exists.
#
# Best-effort: warns and skips if pandoc / a PDF engine / poppler is missing, or
# if an individual theme fails to render (leaving any existing thumbnail intact),
# so signing never blocks on preview tooling.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v pandoc >/dev/null 2>&1 || ! command -v pdftoppm >/dev/null 2>&1; then
    echo "render_all_previews: pandoc/poppler not installed — skipping previews." >&2
    exit 0
fi

shopt -s nullglob
for manifest in packs/*/klippster.json; do
    dir="$(dirname "$manifest")"
    id="$(basename "$dir")"
    provider="$(python3 -c "import json; print(json.load(open('$manifest')).get('provider',''))" 2>/dev/null || echo)"
    is_pdf="$(python3 -c "import json; print('pdf' in (json.load(open('$manifest')).get('outputs') or []))" 2>/dev/null || echo False)"
    [ "$provider" = "template" ] && [ "$is_pdf" = "True" ] || continue

    echo "rendering preview for $id ..."
    mkdir -p "previews/$id"
    if ! python3 scripts/render_preview.py "$dir" "previews/$id/sample.png"; then
        echo "warning: preview render failed for $id — keeping any existing thumbnail." >&2
    fi
done
