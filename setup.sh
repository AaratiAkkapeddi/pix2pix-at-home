#!/usr/bin/env bash
# Clones affinelayer/pix2pix-tensorflow and patches it to run its TF1
# graph-mode code through tf.compat.v1 on a modern TensorFlow 2.x install.
# Safe to re-run.
set -euo pipefail

cd "$(dirname "$0")"

echo "==> Cloning affinelayer/pix2pix-tensorflow into vendor/"
if [ ! -d vendor/pix2pix-tensorflow ]; then
  mkdir -p vendor
  git clone https://github.com/affinelayer/pix2pix-tensorflow.git vendor/pix2pix-tensorflow
else
  echo "    vendor/pix2pix-tensorflow already exists, skipping clone"
fi

echo "==> Applying TF2 compat.v1 patches"
bash scripts/apply_patches.sh

echo "==> Setup complete."
echo "    Next: cp config.example.env config.env, edit it, then run"
echo "    scripts/resize_images.py, scripts/combine_pairs.py, scripts/train.sh"
