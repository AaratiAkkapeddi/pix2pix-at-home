#!/usr/bin/env bash
# Patches the vendored pix2pix-tensorflow repo to run under TensorFlow 2.x
# via tf.compat.v1, instead of requiring the (Apple-Silicon-unavailable)
# tensorflow==1.15 wheel.
#
# NOTE: macOS ships BSD sed, which requires an explicit backup extension for
# -i (`sed -i.bak ...`). GNU sed (Linux/Colab) accepts `sed -i ...` with no
# extension. Don't copy sed one-liners from the original Colab notebook
# straight onto a Mac — they will fail or behave differently.
set -euo pipefail

cd "$(dirname "$0")/.."
REPO=vendor/pix2pix-tensorflow

if [ ! -d "$REPO" ]; then
  echo "error: $REPO not found — run setup.sh first" >&2
  exit 1
fi

patch_file() {
  local f="$1"
  if [ ! -f "$f" ]; then
    echo "  (skip, not found) $f"
    return
  fi
  if grep -q "tf.disable_v2_behavior" "$f"; then
    echo "  already patched: $f"
    return
  fi
  sed -i.bak 's/^import tensorflow as tf$/import tensorflow.compat.v1 as tf\
tf.disable_v2_behavior()/' "$f"
  rm -f "$f.bak"
  echo "  patched: $f"
}

echo "Patching vendored files for tf.compat.v1..."
patch_file "$REPO/pix2pix.py"
patch_file "$REPO/server/tools/export-checkpoint.py"
patch_file "$REPO/server/tools/dump_checkpoints/tensorflow_checkpoint_dumper.py"
echo "Done."
