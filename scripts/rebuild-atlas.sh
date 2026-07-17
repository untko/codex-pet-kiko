#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$script_dir/.." && pwd)"
run_dir="$repo_dir/run"
codex_dir="${CODEX_HOME:-$HOME/.codex}"

if [[ -d "$codex_dir/skills/hatch-pet/scripts" ]]; then
  hatch_scripts="$codex_dir/skills/hatch-pet/scripts"
elif [[ -d "$codex_dir/vendor_imports/skills/skills/.curated/hatch-pet/scripts" ]]; then
  hatch_scripts="$codex_dir/vendor_imports/skills/skills/.curated/hatch-pet/scripts"
else
  echo "Could not find the hatch-pet scripts under $codex_dir" >&2
  exit 1
fi

mkdir -p "$run_dir/final" "$run_dir/qa/previews" "$run_dir/v2/final" "$run_dir/v2/qa"

python_bin="${PYTHON:-}"
if [[ -z "$python_bin" ]]; then
  python_bin="$(command -v python3 || true)"
fi
if [[ -z "$python_bin" ]]; then
  echo "Set PYTHON to a Python executable with Pillow installed" >&2
  exit 1
fi

v1_png="$run_dir/final/spritesheet.png"
v1_webp="$run_dir/final/spritesheet.webp"
v1_validation="$run_dir/final/validation.json"
v2_atlas="$repo_dir/kiko/spritesheet.webp"
v2_dir="$run_dir/v2"
build_dir="$(mktemp -d "${TMPDIR:-/tmp}/kiko-rebuild.XXXXXX")"
trap 'rm -rf "$build_dir"' EXIT

"$python_bin" "$hatch_scripts/inspect_frames.py" \
  --frames-root "$run_dir/frames" \
  --json-out "$run_dir/qa/review.json" \
  --require-components

"$python_bin" "$hatch_scripts/compose_atlas.py" \
  --frames-root "$run_dir/frames" \
  --output "$build_dir/spritesheet-standard.png" \
  --webp-output "$build_dir/spritesheet-standard.webp"

"$python_bin" "$hatch_scripts/despill_chroma_edges.py" \
  "$build_dir/spritesheet-standard.png" \
  --output "$v1_png" \
  --webp-output "$v1_webp" \
  --json-out "$run_dir/qa/chroma-despill.json" \
  --chroma-key '#FF00FF'

"$python_bin" "$hatch_scripts/validate_atlas.py" \
  "$v1_webp" \
  --json-out "$v1_validation" \
  --chroma-key '#FF00FF'

"$python_bin" "$hatch_scripts/make_contact_sheet.py" \
  "$v1_webp" \
  --output "$run_dir/qa/contact-sheet.png"

"$python_bin" "$hatch_scripts/render_animation_previews.py" \
  --frames-root "$run_dir/frames" \
  --output-dir "$run_dir/qa/previews"

"$python_bin" "$hatch_scripts/assemble_extended_atlas.py" \
  --base-atlas "$v1_webp" \
  --look-cells-dir "$v2_dir/look-cells" \
  --neutral-cell "$v2_dir/neutral.png" \
  --output "$build_dir/spritesheet-v2.png" \
  --webp-output "$build_dir/spritesheet-v2.webp" \
  --manifest-output "$v2_dir/final/spritesheet-extended.json" \
  --chroma-key '#FF00FF' \
  --chroma-threshold 96

"$python_bin" "$hatch_scripts/despill_chroma_edges.py" \
  "$build_dir/spritesheet-v2.png" \
  --output "$v2_dir/final/spritesheet.png" \
  --webp-output "$v2_atlas" \
  --json-out "$v2_dir/qa/chroma-despill.json" \
  --chroma-key '#FF00FF'

"$python_bin" "$hatch_scripts/validate_atlas.py" \
  "$v2_atlas" \
  --json-out "$v2_dir/validation.json" \
  --chroma-key '#FF00FF' \
  --require-v2

"$python_bin" "$hatch_scripts/make_contact_sheet.py" \
  "$v2_atlas" \
  --output "$v2_dir/qa/contact-sheet.png"

"$python_bin" "$hatch_scripts/make_direction_qa_sheet.py" \
  "$v2_atlas" \
  --output "$v2_dir/qa/look-directions.png"

echo "Rebuilt Kiko's 8x9 standard intermediate and packaged 8x11 v2 atlas"
