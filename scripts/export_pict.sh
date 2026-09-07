#!/usr/bin/env bash
# Freeze the trained checkpoint and export it as a .pict file, for use with
# the pix2pix interactive web demo.
#
# Unlike the original Colab notebook, this does NOT `pip install tensorflow==1.15`
# first — that wheel isn't available on Apple Silicon. It relies entirely on
# the tf.compat.v1 patches applied by scripts/apply_patches.sh, using the same
# TensorFlow install as training.
set -euo pipefail

cd "$(dirname "$0")/.."
set -a; source config.env; set +a

REPO=vendor/pix2pix-tensorflow
EXPORT_DIR=export

mkdir -p "$EXPORT_DIR"
mkdir -p "$(dirname "$PICT_OUTPUT")"

echo "==> Freezing checkpoint from $CKPT_DIR"
TF_USE_LEGACY_KERAS=1 python "$REPO/pix2pix.py" \
  --mode export \
  --output_dir "$EXPORT_DIR/" \
  --checkpoint "$CKPT_DIR" \
  --which_direction "${WHICH_DIRECTION:-AtoB}"

echo "==> Converting to .pict"
TF_USE_LEGACY_KERAS=1 python "$REPO/server/tools/export-checkpoint.py" \
  --checkpoint "$EXPORT_DIR/" \
  --output_file "$PICT_OUTPUT"

echo "==> Done: $PICT_OUTPUT"
