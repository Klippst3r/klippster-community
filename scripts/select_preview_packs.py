#!/usr/bin/env python3
"""From a list of changed paths on stdin, print a JSON array of the template
PDF-theme pack ids whose *render-relevant* files changed — so preview CI only
re-renders when the manifest, the template, or the sample changed (not the
README or unrelated files).
"""
import glob
import json
import os
import sys

# Files that actually affect the rendered preview.
RENDER_RELEVANT = {"klippster.json", "sample.md"}
# Shared inputs whose change re-renders EVERY theme pack (not just ones with pack-file changes).
SHARED_INPUTS = {"previews/sample.md", "scripts/render_preview.py", "scripts/select_preview_packs.py"}


def all_theme_packs():
    ids = []
    for manifest_path in glob.glob("packs/*/klippster.json"):
        try:
            manifest = json.load(open(manifest_path))
        except (ValueError, OSError):
            continue
        if manifest.get("provider") == "template" and "pdf" in (manifest.get("outputs") or []):
            ids.append(os.path.basename(os.path.dirname(manifest_path)))
    return sorted(ids)


def main():
    changed = [line.strip() for line in sys.stdin if line.strip()]

    # A change to the canonical sample or the render script affects every theme's preview.
    if any(path in SHARED_INPUTS for path in changed):
        print(json.dumps(all_theme_packs()))
        return

    files_by_pack = {}
    for path in changed:
        parts = path.split("/")
        if len(parts) >= 2 and parts[0] == "packs":
            files_by_pack.setdefault(parts[1], set()).add("/".join(parts[2:]))

    selected = []
    for pack_id, files in sorted(files_by_pack.items()):
        manifest_path = os.path.join("packs", pack_id, "klippster.json")
        if not os.path.isfile(manifest_path):
            continue  # pack was deleted
        try:
            manifest = json.load(open(manifest_path))
        except (ValueError, OSError):
            continue
        if manifest.get("provider") != "template" or "pdf" not in (manifest.get("outputs") or []):
            continue  # only PDF theme packs have a rendered preview
        relevant = set(RENDER_RELEVANT)
        template = (manifest.get("options") or {}).get("template")
        if template:
            relevant.add(template)
        if files & relevant:
            selected.append(pack_id)

    print(json.dumps(selected))


if __name__ == "__main__":
    main()
