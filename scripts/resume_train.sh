#!/usr/bin/env bash
# Resume training from the last checkpoint in CKPT_DIR (does NOT wipe it).
set -euo pipefail

cd "$(dirname "$0")/.."
set -a; source config.env; set +a

REPO=vendor/pix2pix-tensorflow

if [ ! -d "$CKPT_DIR" ]; then
  echo "error: $CKPT_DIR does not exist yet — run scripts/train.sh first" >&2
  exit 1
fi

TF_USE_LEGACY_KERAS=1 python "$REPO/pix2pix.py" \
  --mode train \
  --input_dir "$COMBINED_DIR" \
  --output_dir "$CKPT_DIR" \
  --which_direction "${WHICH_DIRECTION:-AtoB}" \
  --max_epochs "${MAX_EPOCHS:-200}" \
  --lr "${LR:-0.0001}" \
  --save_freq "${SAVE_FREQ:-100}" \
  --display_freq "${DISPLAY_FREQ:-500}" \
  --checkpoint "$CKPT_DIR"
