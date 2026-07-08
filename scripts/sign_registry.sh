#!/usr/bin/env bash
#
# Sign registry.json with the maintainer's offline Ed25519 key (issue #16).
#
# Regenerates registry.json from packs/, then writes a detached raw-64-byte Ed25519
# signature to registry.json.sig. The Klippster app pins the matching public key and
# verifies this signature before trusting any checksum inside registry.json.
#
# Offline signing: the private key stays on the maintainer's machine and is never
# committed (see .gitignore) nor uploaded to CI. Run this at release time, then commit
# BOTH registry.json and registry.json.sig.
#
# Requires OpenSSL 3 for Ed25519 `pkeyutl -rawin`. macOS /usr/bin/openssl is LibreSSL
# and will NOT work — install `brew install openssl@3` (this script auto-detects it).
#
# Usage:
#   scripts/sign_registry.sh
#   PRIVATE_KEY=/path/to/registry_signing_key.pem scripts/sign_registry.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PRIVATE_KEY="${PRIVATE_KEY:-registry_signing_key.pem}"
PUBLIC_KEY="${PUBLIC_KEY:-keys/registry_signing_pub.pem}"
REGISTRY="registry.json"
SIGNATURE="registry.json.sig"

# --- Resolve an OpenSSL 3 binary (not LibreSSL) ---------------------------------------
find_openssl() {
    for candidate in "${OPENSSL:-}" \
        /opt/homebrew/bin/openssl \
        /usr/local/opt/openssl@3/bin/openssl \
        /opt/homebrew/opt/openssl@3/bin/openssl \
        openssl; do
        [ -n "$candidate" ] || continue
        command -v "$candidate" >/dev/null 2>&1 || continue
        if "$candidate" version 2>/dev/null | grep -q '^OpenSSL 3'; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

if ! OPENSSL="$(find_openssl)"; then
    echo "error: need OpenSSL 3 for Ed25519 signing." >&2
    echo "       macOS /usr/bin/openssl is LibreSSL and won't work." >&2
    echo "       Install it (brew install openssl@3) or set OPENSSL=/path/to/openssl3." >&2
    exit 1
fi
echo "using $($OPENSSL version) at $OPENSSL"

if [ ! -f "$PRIVATE_KEY" ]; then
    echo "error: private key '$PRIVATE_KEY' not found." >&2
    echo "       It's held offline and gitignored; restore it before signing, or set PRIVATE_KEY=..." >&2
    exit 1
fi

# --- Refresh theme-pack preview thumbnails (best-effort) ------------------------------
# Renders previews/<id>/sample.png for each PDF theme pack, so build_registry.py can attach each
# pack's `preview` URL and the thumbnails ship inside this signed release. Skips silently if the
# render tooling (pandoc + a PDF engine + poppler) isn't installed.
echo "refreshing theme previews ..."
scripts/render_all_previews.sh || true

# --- Regenerate the index and advance the anti-rollback serial ------------------------
# --bump increments registrySerial so this signed release supersedes the previous one; the
# client refuses any index whose serial is lower than the highest it has already trusted.
echo "regenerating + bumping $REGISTRY ..."
python3 scripts/build_registry.py --bump

# --- Sign the exact bytes on disk (raw Ed25519, no pre-hash) --------------------------
echo "signing $REGISTRY -> $SIGNATURE ..."
"$OPENSSL" pkeyutl -sign -inkey "$PRIVATE_KEY" -rawin -in "$REGISTRY" -out "$SIGNATURE"

# --- Self-verify so a bad signature fails loudly here, not in the app -----------------
if [ -f "$PUBLIC_KEY" ]; then
    "$OPENSSL" pkeyutl -verify -pubin -inkey "$PUBLIC_KEY" -rawin \
        -in "$REGISTRY" -sigfile "$SIGNATURE" >/dev/null
    echo "ok: signature verifies against $PUBLIC_KEY"
else
    echo "warning: public key '$PUBLIC_KEY' not found — skipped self-verify." >&2
fi

echo "done. Commit BOTH $REGISTRY and $SIGNATURE."
