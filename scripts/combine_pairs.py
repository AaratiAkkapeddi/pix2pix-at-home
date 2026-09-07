#!/usr/bin/env python3
"""Combine resized A/B pairs into 512x256 side-by-side images pix2pix trains on
(A on the left, B on the right). Run scripts/resize_images.py first.

    python scripts/combine_pairs.py [--preview]
"""
import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

load_dotenv("config.env")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--a-resized", default=os.environ.get("A_RESIZED", "data/A_resized")
    )
    parser.add_argument(
        "--b-resized", default=os.environ.get("B_RESIZED", "data/B_resized")
    )
    parser.add_argument(
        "--out-dir", default=os.environ.get("COMBINED_DIR", "data/combined")
    )
    parser.add_argument(
        "--preview", action="store_true", help="Show the first combined pair with matplotlib"
    )
    args = parser.parse_args()

    a_resized = Path(args.a_resized)
    b_resized = Path(args.b_resized)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    a_files = sorted(f for f in os.listdir(a_resized) if f.lower().endswith(".png"))

    combined_count = 0
    skipped = []

    for fname in a_files:
        a_path = a_resized / fname
        b_path = b_resized / fname  # same filename in B folder

        if not b_path.exists():
            skipped.append(fname)
            continue

        img_a = Image.open(a_path).convert("RGB")
        img_b = Image.open(b_path).convert("RGB")

        combined = Image.new("RGB", (512, 256))
        combined.paste(img_a, (0, 0))  # A on the LEFT (input)
        combined.paste(img_b, (256, 0))  # B on the RIGHT (target)

        combined.save(out_dir / fname)
        combined_count += 1

    print(f"Combined {combined_count} image pairs -> {out_dir}")
    if skipped:
        print(f"Skipped {len(skipped)} A images with no matching B file: {skipped[:5]}")

    if args.preview and combined_count > 0:
        import matplotlib.pyplot as plt

        sample = Image.open(out_dir / a_files[0])
        plt.figure(figsize=(10, 4))
        plt.imshow(sample)
        plt.axis("off")
        plt.title(f"Sample combined image: {a_files[0]} (A left | B right)")
        plt.show()


if __name__ == "__main__":
    main()
