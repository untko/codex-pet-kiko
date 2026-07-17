#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$script_dir/.." && pwd)"
codex_dir="${CODEX_HOME:-$HOME/.codex}"
pet_dir="$codex_dir/pets/kiko"

mkdir -p "$pet_dir"
cp "$repo_dir/kiko/pet.json" "$pet_dir/pet.json"
cp "$repo_dir/kiko/spritesheet.webp" "$pet_dir/spritesheet.webp"

echo "Installed Kiko in $pet_dir"

