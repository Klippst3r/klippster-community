#!/usr/bin/env bash
#
# Sign and publish the pack registry in one step.
#
# Renders theme previews, regenerates + bumps + Ed25519-signs registry.json, then commits and
# pushes registry.json + registry.json.sig + previews/ on the CURRENT branch — which turns a pull
# request's "Verify registry signature" check green.
#
# The offline private key is read from ~/.secrets/klippster_private_key (override with
# KLIPPSTER_SIGNING_KEY=/path/to/key). It is never committed.
#
# Usage:
#   scripts/sign_and_publish.sh                       # sign, commit, push (default message)
#   scripts/sign_and_publish.sh "Sign v3 theme packs" # custom commit message
#   scripts/sign_and_publish.sh --no-push             # sign + commit, but don't push
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

KEY_PATH="${KLIPPSTER_SIGNING_KEY:-$HOME/.secrets/klippster_private_key}"

if [ ! -f "$KEY_PATH" ]; then
  echo "✗ Signing key not found at: $KEY_PATH" >&2
  echo >&2
  echo "  This is the offline Ed25519 private key that signs registry.json." >&2
  echo "  Put it there once and lock it down:" >&2
  echo >&2
  echo "      mkdir -p ~/.secrets && chmod 700 ~/.secrets" >&2
  echo "      cp /path/to/registry_signing_key.pem ~/.secrets/klippster_private_key" >&2
  echo "      chmod 600 ~/.secrets/klippster_private_key" >&2
  echo >&2
  echo "  Or point elsewhere with KLIPPSTER_SIGNING_KEY=/path/to/key. Never commit the key." >&2
  exit 1
fi

push=1
msg="Sign and publish registry"
for arg in "$@"; do
  case "$arg" in
    --no-push) push=0 ;;
    *) msg="$arg" ;;
  esac
done

echo "→ Signing with key: $KEY_PATH"
PRIVATE_KEY="$KEY_PATH" scripts/sign_registry.sh

git add registry.json registry.json.sig previews/
if git diff --cached --quiet; then
  echo "✓ Already up to date — registry.json and previews unchanged, nothing to publish."
  exit 0
fi

echo
echo "→ Staged:"
git diff --cached --name-only | sed 's/^/    /'
git commit -q -m "$msg"
echo "✓ Committed: $msg"

if [ "$push" -eq 1 ]; then
  branch="$(git rev-parse --abbrev-ref HEAD)"
  git push origin "$branch"
  echo "✓ Pushed to origin/$branch — the signature check will re-run and go green."
else
  echo "ℹ Skipped push (--no-push). Push when ready:  git push"
fi
