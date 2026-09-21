
## put your B folder of images in the 'data' folder


## Crop B images to centered squares and optionally add horizontally flipped copies.

```bash
     python scripts/square_flip.py --input data/B --output data/B_processed  --flip
```
## Generate an "A" dataset from your B folder of images by running this edge detection script...

```bash
pip install opencv-python-headless
  # preview a few first to tune thresholds
python scripts/generate_edges.py --input data/B --output data/A  --limit 10
```
## You can update the threshold by adding these flags
`--low-threshold` and  `--high-threshold`  
example:
```bash
python scripts/generate_edges.py --input data/B --output data/A  --low-threshold 30 --high-threshold 100 --limit 10
```
## when it looks good run the full batch (if you ended up using the threshold flags, make sure to add them below too):
```bash
python scripts/generate_edges.py --input path/to/B/folder --output path/to/A/folder
```

# pix2pix — local training on Apple Silicon Mac

trains a pix2pix image-to-image model on your own paired
A/B image folders and exports a `.pict` file

If you want to run this training in Google Colab go here -> https://colab.research.google.com/drive/1l3bhWi1wpkKazHEP5qdvXWbFBxqtZtBE?usp=drive_link


## 1. Requirements

- A Mac with Apple Silicon (M1/M2/M3/M4)
- Xcode Command Line Tools: `xcode-select --install`
- Python 3.10 or 3.11 (recommend via [pyenv](https://github.com/pyenv/pyenv) or
  [miniconda](https://docs.conda.io/en/latest/miniconda.html) — the system Python
  on macOS is not a good fit for this)
- `git`

## 2. Set up the environment
From inside this repo

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Clones affinelayer/pix2pix-tensorflow into vendor/ and patches it for TF2 compat.v1
bash setup.sh
```

Optional GPU acceleration: uncomment `tensorflow-metal` in `requirements.txt` and
reinstall. This is genuinely optional and sometimes unstable with this codebase,
since it's old graph-mode TF1 code running through a compatibility shim — see
**Troubleshooting** below if training hangs, crashes, or produces NaNs on the GPU.
CPU training works fine for small/medium datasets, just slower.

## 3. Configure your paths

```bash
cp config.example.env config.env
```

Edit `config.env`:

```
A_DIR=./data/A              # your source/input images
B_DIR=./data/B              # your target/output images (same filenames as A)
COMBINED_DIR=./data/combined
CKPT_DIR=./checkpoints/my_model
PICT_OUTPUT=./models/my_custom_model.pict

WHICH_DIRECTION=AtoB
MAX_EPOCHS=200
LR=0.0001
SAVE_FREQ=100
DISPLAY_FREQ=500
```

`A_DIR` and `B_DIR` must contain images with **matching filenames** (e.g.
`A/leaf001.jpg` pairs with `B/leaf001.jpg`).


## 4. Prepare the data

Resize everything to 256×256 and stitch each A/B pair into a single
512×256 side-by-side image (A left, B right — what pix2pix trains on):

```bash
python scripts/resize_images.py
python scripts/combine_pairs.py
```

## 5. Train

```bash
pip install tf_keras
bash scripts/train.sh
```
Note that each checkpoint is around ~700MB so be wary of how much space you have on your computer.
This repo is set up so that only the latest checkpoint is saved so you should not need to periodically delete older checkpoints.

This wipes `CKPT_DIR` and starts fresh. To resume an interrupted run instead:

```bash
bash scripts/resume_train.sh
```

For local experiments, start with a small dataset (a few hundred pairs) and/or
a lower `MAX_EPOCHS` in `config.env` before committing to a long run.

## 6. Export to `.pict`

```bash
bash scripts/export_pict.sh
```

This freezes the checkpoint and converts it to `models/my_custom_model.pict`
(or wherever `PICT_OUTPUT` points). That file is what the [pix2pix interactive
web demo](https://handmadedatasets.com/pix2pixuploaddemo/) loads to run inference in the browser.

## Troubleshooting

**`AttributeError` mentioning `NewCheckpointReader` during export**
Already patched for you by `setup.sh` — `scripts/apply_patches.sh` applies the
same TF2-compat fix the original notebook applies manually in its "Fix TF1
compatibility" cell. If you still hit this, re-run:
```bash
bash scripts/apply_patches.sh
```

**Training hangs, crashes, or loss becomes `NaN` with `tensorflow-metal` installed**
Uninstall it and fall back to CPU OR check if maybe your model is good enough already.:
```bash
pip uninstall tensorflow-metal
```
Old graph-mode TF1 ops (via `tf.compat.v1`) aren't all well supported by the
Metal plugin. CPU is the reliable path for this specific codebase.

**`sed` errors when re-running patches manually**
macOS ships BSD `sed`, which needs an explicit backup extension for `-i`
(`sed -i.bak ...`), unlike Linux/Colab's GNU `sed`. `scripts/apply_patches.sh`
already accounts for this — don't copy `sed` commands straight from the
original Colab notebook.

**`numpy` errors about deprecated/removed attributes**
`requirements.txt` pins `numpy<2` on purpose — this TF1-era code isn't
NumPy-2.0-safe. Don't upgrade it independently.

## Repo layout

```
├── setup.sh                  # clones + patches vendor/pix2pix-tensorflow
├── config.example.env        # copy to config.env and edit
├── requirements.txt
├── scripts/
│   ├── apply_patches.sh      # TF2 compat.v1 patches (called by setup.sh)
│   ├── resize_images.py      # step 1: resize A/B folders to 256x256
│   ├── combine_pairs.py      # step 2: stitch A/B into 512x256 pairs
│   ├── train.sh              # step 3: train from scratch
│   ├── resume_train.sh       # step 3b: resume an interrupted run
│   └── export_pict.sh        # step 4: freeze + export .pict
└── vendor/                   # created by setup.sh, not checked in
```
