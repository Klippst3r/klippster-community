#!/usr/bin/env python3
"""Generate and validate registry.json from the packs/ tree.

Git-based distribution (no backend): every pack is a folder under packs/<id>/ containing a
klippster.json manifest and its files. This script walks that tree, validates each manifest,
checksums every file, and writes a single registry.json index the Klippster app fetches.

Output is deterministic (sorted, no timestamps) so CI can run `--check` to verify the committed
registry.json matches the packs tree. Standard library only — no third-party deps.

Usage:
  build_registry.py            # regenerate registry.json
  build_registry.py --check    # exit non-zero if registry.json is stale or a pack is invalid
"""
import argparse
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS_DIR = os.path.join(REPO_ROOT, "packs")
REGISTRY_PATH = os.path.join(REPO_ROOT, "registry.json")
SCHEMA_VERSION = 1

# Raw base for file download URLs. Update if the repo is renamed/moved.
RAW_BASE = "https://raw.githubusercontent.com/Klippst3r/klippster-community/main"

# Provider → the manifest field that names its payload (mirrors PackManifest.validate in the app).
PROVIDER_PAYLOAD_FIELD = {"native": "engine", "host": "binary", "template": "engine", "wasm": "module"}


class PackError(Exception):
    pass


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(pack_dir):
    manifest_path = os.path.join(pack_dir, "klippster.json")
    if not os.path.isfile(manifest_path):
        raise PackError("missing klippster.json")
    try:
        with open(manifest_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise PackError(f"klippster.json is not valid JSON: {exc}")


def validate_manifest(manifest, folder_name):
    for field in ("id", "name", "version", "provider", "inputs", "outputs"):
        if not manifest.get(field):
            raise PackError(f"manifest field '{field}' is required and must not be empty")
    if manifest["id"] != folder_name:
        raise PackError(f"manifest id '{manifest['id']}' must match its folder name '{folder_name}'")
    provider = manifest["provider"]
    if provider not in PROVIDER_PAYLOAD_FIELD:
        raise PackError(f"unknown provider '{provider}'")
    payload_field = PROVIDER_PAYLOAD_FIELD[provider]
    if not manifest.get(payload_field):
        raise PackError(f"provider '{provider}' requires the '{payload_field}' field")
    if not isinstance(manifest["inputs"], list) or not isinstance(manifest["outputs"], list):
        raise PackError("inputs and outputs must be arrays")
    # For wasm, the named module file must actually exist in the pack folder.
    if provider == "wasm":
        module = manifest["module"]
        if "/" in module or module.startswith(".."):
            raise PackError(f"module '{module}' must be a bare filename inside the pack folder")
    # For a template pack that ships a template file (e.g. a pandoc LaTeX theme), it must be a
    # bare filename inside the pack folder — same rule as the wasm module.
    if provider == "template":
        template = (manifest.get("options") or {}).get("template")
        if template and ("/" in template or template.startswith("..")):
            raise PackError(f"template '{template}' must be a bare filename inside the pack folder")


def build_pack_entry(pack_dir, folder_name):
    manifest = load_manifest(pack_dir)
    validate_manifest(manifest, folder_name)

    if manifest["provider"] == "wasm":
        module_path = os.path.join(pack_dir, manifest["module"])
        if not os.path.isfile(module_path):
            raise PackError(f"module file '{manifest['module']}' not found in the pack folder")

    if manifest["provider"] == "template":
        template = (manifest.get("options") or {}).get("template")
        if template:
            template_path = os.path.join(pack_dir, template)
            if not os.path.isfile(template_path):
                raise PackError(f"template file '{template}' not found in the pack folder")

    rel_pack = f"packs/{folder_name}"
    files = []
    for name in sorted(os.listdir(pack_dir)):
        full = os.path.join(pack_dir, name)
        if not os.path.isfile(full) or name.startswith("."):
            continue
        files.append({
            "name": name,
            "sha256": sha256_file(full),
            "url": f"{RAW_BASE}/{rel_pack}/{name}",
        })

    return {
        "id": manifest["id"],
        "name": manifest["name"],
        "version": manifest["version"],
        "description": manifest.get("description", ""),
        "author": manifest.get("author", ""),
        "license": manifest.get("license", ""),
        "provider": manifest["provider"],
        "inputs": manifest["inputs"],
        "outputs": manifest["outputs"],
        "path": rel_pack,
        "files": files,
    }


def read_current_serial():
    """The registrySerial already committed in registry.json (0 if none/unreadable).

    Preserved across regeneration so a plain rebuild is byte-identical (--check stays deterministic);
    it advances only on an explicit --bump at release time. See build_registry / sign_registry.sh.
    """
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return int(json.load(f).get("registrySerial", 0))
    except (FileNotFoundError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def build_registry(bump=False):
    # Monotonic anti-rollback serial. Bumping advances it (min 1); a plain build preserves the
    # committed value (floored to 1) so regeneration is reproducible.
    current_serial = read_current_serial()
    serial = current_serial + 1 if bump else max(current_serial, 1)

    if not os.path.isdir(PACKS_DIR):
        return {"registrySerial": serial, "schemaVersion": SCHEMA_VERSION, "packs": []}, []

    packs, errors, seen_ids = [], [], set()
    for folder_name in sorted(os.listdir(PACKS_DIR)):
        pack_dir = os.path.join(PACKS_DIR, folder_name)
        if not os.path.isdir(pack_dir) or folder_name.startswith("."):
            continue
        try:
            entry = build_pack_entry(pack_dir, folder_name)
        except PackError as exc:
            errors.append(f"packs/{folder_name}: {exc}")
            continue
        if entry["id"] in seen_ids:
            errors.append(f"packs/{folder_name}: duplicate pack id '{entry['id']}'")
            continue
        seen_ids.add(entry["id"])
        packs.append(entry)

    return {"registrySerial": serial, "schemaVersion": SCHEMA_VERSION, "packs": packs}, errors


def dumps(registry):
    # Deterministic: stable key order, trailing newline, no timestamps.
    return json.dumps(registry, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate/validate registry.json from packs/.")
    parser.add_argument("--check", action="store_true",
                        help="verify registry.json is up to date and all packs are valid; no write")
    parser.add_argument("--bump", action="store_true",
                        help="advance registrySerial by 1 (do this at release time, before signing)")
    args = parser.parse_args()

    # --check must never bump — it has to compare against the committed serial, not a new one.
    registry, errors = build_registry(bump=args.bump and not args.check)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        return 1

    rendered = dumps(registry)

    if args.check:
        try:
            with open(REGISTRY_PATH, encoding="utf-8") as f:
                current = f.read()
        except FileNotFoundError:
            current = None
        if current != rendered:
            print("error: registry.json is out of date — run scripts/build_registry.py and commit.",
                  file=sys.stderr)
            return 1
        print(f"ok: registry.json is current ({len(registry['packs'])} pack(s)).")
        return 0

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        f.write(rendered)
    print(f"wrote registry.json ({len(registry['packs'])} pack(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
