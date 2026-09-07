#!/usr/bin/env python3
"""Resize the A (input) and B (target) image folders to 256x256 PNGs.

Reads paths from config.env by default. Override with flags if you want:

    python scripts/resize_images.py --a-dir data/A --b-dir data/B
"""
import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

load_dotenv("config.env")

TARGET_SIZE = (256, 256)
VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}


def resize_folder(src_dir: Path, dst_dir: Path, label: str) -> list[str]:
    dst_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(
        f for f in os.listdir(src_dir) if Path(f).suffix.lower() in VALID_EXTS
    )
    print(f"Resizing {len(files)} {label} images...")
    for fname in files:
        img = Image.open(src_dir / fname).convert("RGB")
        img = img.resize(TARGET_SIZE, Image.LANCZOS)
        img.save(dst_dir / (Path(fname).stem + ".png"))
    print(f"  done -> {dst_dir}")
    return files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a-dir", default=os.environ.get("A_DIR"))
    parser.add_argument("--b-dir", default=os.environ.get("B_DIR"))
    parser.add_argument(
        "--a-out", default=os.environ.get("A_RESIZED", "data/A_resized")
    )
    parser.add_argument(
        "--b-out", default=os.environ.get("B_RESIZED", "data/B_resized")
    )
    args = parser.parse_args()

    if not args.a_dir or not args.b_dir:
        parser.error(
            "A_DIR and B_DIR are not set. Either pass --a-dir/--b-dir, or "
            "create config.env from config.example.env."
        )

    a_files = resize_folder(Path(args.a_dir), Path(args.a_out), "A")
    b_files = resize_folder(Path(args.b_dir), Path(args.b_out), "B")

    a_stems = {Path(f).stem for f in a_files}
    b_stems = {Path(f).stem for f in b_files}
    missing = a_stems.symmetric_difference(b_stems)
    if missing:
        print(
            f"WARNING: {len(missing)} filenames appear in only one folder: "
            f"{sorted(missing)[:10]}"
        )
    else:
        print(f"All {len(a_stems)} filenames match between A and B. Ready to combine.")


if __name__ == "__main__":
    main()
