#!/usr/bin/env bash
# Generate browser favicon assets and an Apple touch icon from the UChicago shield.
# Requires ImageMagick's `magick` command; generated files are written to `static/`.
set -euo pipefail

# Resolve all paths from the repository root so the script works from any directory.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_image="$repo_root/assets/favicon/UChicago_Shield_Maroon.png"
output_dir="$repo_root/static"
work_dir="$(mktemp -d)"

# Remove intermediate favicon sizes when the script exits.
trap 'rm -rf "$work_dir"' EXIT

if ! command -v magick >/dev/null 2>&1; then
  echo "ImageMagick's magick command is required." >&2
  exit 1
fi

render_transparent() {
  local canvas_size="$1"
  local shield_height="$2"
  local output_file="$3"

  # Center the trimmed shield on a transparent square canvas.
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

# Render the PNG sizes used directly and in the multi-resolution ICO file.
render_transparent 16 14 "$work_dir/favicon-16x16.png"
render_transparent 32 29 "$output_dir/favicon-32x32.png"
render_transparent 48 43 "$work_dir/favicon-48x48.png"

# Bundle the standard favicon sizes into a single ICO file.
magick \
  "$work_dir/favicon-16x16.png" \
  "$output_dir/favicon-32x32.png" \
  "$work_dir/favicon-48x48.png" \
  "$output_dir/favicon.ico"

# Create the larger Apple touch icon on an opaque white canvas.
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
