#!/usr/bin/env bash
# Resolve-check server/render_requirements.txt without polluting the repo.
# Usage: from repo root: ./server/scripts/verify_render_requirements.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REQ="$ROOT/server/render_requirements.txt"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/wort-pipcheck.XXXXXX")"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

# Prefer 3.11 to match Render; fall back to whatever `python3` is.
if command -v python3.11 >/dev/null 2>&1; then
  PY=python3.11
else
  PY=python3
fi
echo "Using: $(command -v "$PY") — $($PY --version)"
"$PY" -m venv "$TMP/venv"
"$TMP/venv/bin/pip" install -q -U pip setuptools wheel
echo "Running: pip install --dry-run -r server/render_requirements.txt"
"$TMP/venv/bin/pip" install --dry-run -r "$REQ"
echo "OK: dependency resolution succeeded (dry-run only; nothing installed in repo)."
