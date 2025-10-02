#!/usr/bin/env bash
set -euo pipefail

# Download directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
FACE_DIR="$ROOT_DIR/face_detecting"
mkdir -p "$FACE_DIR"

echo "Downloading dlib 68 landmarks model (non-commercial use only)..."
# Official dlib mirror URL (users should verify terms before use)
MODEL_URL="http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
TMP_BZ2="$FACE_DIR/shape_predictor_68_face_landmarks.dat.bz2"
OUT_DAT="$FACE_DIR/shape_predictor_68_face_landmarks.dat"

if command -v curl >/dev/null 2>&1; then
  curl -L "$MODEL_URL" -o "$TMP_BZ2"
elif command -v wget >/dev/null 2>&1; then
  wget -O "$TMP_BZ2" "$MODEL_URL"
else
  echo "Error: curl or wget is required to download the model." >&2
  exit 1
fi

echo "Decompressing model..."
if command -v bunzip2 >/dev/null 2>&1; then
  bunzip2 -f "$TMP_BZ2"
else
  echo "Error: bunzip2 is required to decompress .bz2 files." >&2
  exit 1
fi

if [ -f "$OUT_DAT" ]; then
  echo "Model saved to: $OUT_DAT"
  echo "Note: This model is commonly considered non-commercial. Use only for research/education unless you obtain appropriate permissions."
else
  echo "Error: model file not found after decompression." >&2
  exit 1
fi

