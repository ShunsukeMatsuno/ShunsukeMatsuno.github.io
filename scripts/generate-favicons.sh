#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_image="$repo_root/assets/favicon/UChicago_Shield_Maroon.png"
output_dir="$repo_root/static"
work_dir="$(mktemp -d)"

trap 'rm -rf "$work_dir"' EXIT

if ! command -v magick >/dev/null 2>&1; then
  echo "ImageMagick's magick command is required." >&2
  exit 1
fi

render_transparent() {
  local canvas_size="$1"
  local shield_height="$2"
  local output_file="$3"

  magick "$source_image" \
    -trim +repage \
    -filter Lanczos \
    -resize "x${shield_height}" \
    -gravity center \
    -background none \
    -extent "${canvas_size}x${canvas_size}" \
    -strip \
    "$output_file"
}

render_transparent 16 14 "$work_dir/favicon-16x16.png"
render_transparent 32 29 "$output_dir/favicon-32x32.png"
render_transparent 48 43 "$work_dir/favicon-48x48.png"

magick \
  "$work_dir/favicon-16x16.png" \
  "$output_dir/favicon-32x32.png" \
  "$work_dir/favicon-48x48.png" \
  "$output_dir/favicon.ico"

magick "$source_image" \
  -trim +repage \
  -filter Lanczos \
  -resize "x144" \
  -gravity center \
  -background white \
  -extent 180x180 \
  -alpha remove \
  -alpha off \
  -strip \
  "$output_dir/apple-touch-icon.png"
