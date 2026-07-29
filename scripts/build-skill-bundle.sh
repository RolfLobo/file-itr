#!/usr/bin/env bash
# Rebuild itr-india.skill (the one-click-install bundle the README points to)
# from the sources in skills/itr-india/. Deterministic: identical source
# contents produce a byte-identical zip, so `git diff -- itr-india.skill`
# is a reliable freshness check.
set -euo pipefail

# Everything runs in UTC: `touch -t` interprets its timestamp in the local
# timezone and zip stores DOS timestamps in local time, so without this the
# bundle's bytes would differ between machines in different timezones.
export TZ=UTC

cd "$(dirname "$0")/.."
SRC=skills/itr-india
OUT="$PWD/itr-india.skill"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

mkdir -p "$STAGE/itr-india/evals" "$STAGE/itr-india/references"
cp "$SRC/SKILL.md" "$STAGE/itr-india/SKILL.md"
cp "$SRC/evals/evals.json" "$STAGE/itr-india/evals/evals.json"
cp "$SRC"/references/*.md "$STAGE/itr-india/references/"

# Determinism: fixed mtime, no extended attributes (-X), sorted entry order.
find "$STAGE" -exec touch -t 202601010000 {} +
rm -f "$OUT"
(cd "$STAGE" && find itr-india -type f | LC_ALL=C sort | zip -X -q "$OUT" -@)

echo "built $OUT"
