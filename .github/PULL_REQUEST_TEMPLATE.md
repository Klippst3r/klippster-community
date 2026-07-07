<!--
Submitting a Format Pack? Fill in the boxes below. The full contributor guide is CONTRIBUTING.md;
maintainers review against REVIEW_CHECKLIST.md. You do NOT sign anything or touch registrySerial —
the maintainer signs when this lands.
-->

## What this pack does

<!-- One line: e.g. "PDF → Markdown via <library>". Link the source if the .wasm is built from code. -->

## Pack details

- **id:** `com.…`
- **provider:** `wasm` / `template`
- **inputs → outputs:** `…` → `…`
- **license:**

## Contributor checklist

- [ ] Folder name equals the manifest `id`, a reverse-DNS name I control.
- [ ] `klippster.json` has a clear `license`, honest `inputs`/`outputs`, and a `README.md` in the folder.
- [ ] `provider: wasm` requests **no `permissions`** (none are granted yet).
- [ ] I ran `python3 scripts/build_registry.py` and committed **both** the pack folder and the updated
      `registry.json` (I did **not** hand-edit `registry.json`, sign anything, or change `registrySerial`).
- [ ] CI is green (`--check` + schema validation).

<!-- A stale/absent registry.json.sig on your PR is expected — the maintainer re-signs on main. -->
