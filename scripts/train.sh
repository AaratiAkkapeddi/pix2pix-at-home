#!/usr/bin/env bash
# Train pix2pix from scratch. Wipes CKPT_DIR first — use resume_train.sh
# to continue an interrupted run instead.
set -euo pipefail

cd "$(dirname "$0")/.."
set -a; source config.env; set +a

REPO=vendor/pix2pix-tensorflow

echo "==> Starting fresh run — clearing $CKPT_DIR"
rm -rf "$CKPT_DIR"
mkdir -p "$CKPT_DIR"

TF_USE_LEGACY_KERAS=1 python "$REPO/pix2pix.py" \
  --mode train \
  --input_dir "$COMBINED_DIR" \
  --output_dir "$CKPT_DIR" \
  --which_direction "${WHICH_DIRECTION:-AtoB}" \
  --max_epochs "${MAX_EPOCHS:-200}" \
  --lr "${LR:-0.0001}" \
  --save_freq "${SAVE_FREQ:-100}" \
  --display_freq "${DISPLAY_FREQ:-500}"
