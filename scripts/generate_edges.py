#!/usr/bin/env python3
"""
Generate the "A" (edge map) dataset from the "B" (photo) folder, for
pix2pix-style paired training (e.g. edges2flies).

Run this BEFORE resize_images.py / combine_pairs.py — it reads raw photos
from your B folder and writes matching edge maps (same filenames) into
your A folder, which the rest of the pipeline then resizes and pairs as
usual.

Usage:
    python scripts/generate_edges.py
    python scripts/generate_edges.py --input data/flies_B --output data/flies_A
    python scripts/generate_edges.py --low-threshold 30 --high-threshold 100 --limit 10

Tip: edge quality is sensitive to the Canny thresholds and varies a lot by
subject matter. Use --limit 10 (or so) first to preview a handful of edge
maps in the output folder, adjust --low-threshold/--high-threshold, and
re-run before committing to the full dataset.
"""
import argparse
import sys
from pathlib import Path

try:
    import cv2
except ImportError:
    sys.exit(
        "This script needs OpenCV. Install it with:\n"
        "  pip install opencv-python-headless\n"
        "then re-run."
    )
import numpy as np

VALID_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def generate_edge_map(image_path, low_threshold, high_threshold, dilate_iterations, invert):
    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(gray, low_threshold, high_threshold)

    if dilate_iterations > 0:
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=dilate_iterations)

    if invert:
        # black lines on white background — matches the convention used by
        # pix2pix's edges2shoes / edges2handbags datasets
        edges = 255 - edges

    # write back out as 3-channel so it matches the B photos' channel count
    return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--input", default="data/flies_B", help="Folder of source B photos")
    parser.add_argument("--output", default="data/flies_A", help="Folder to write generated A edge maps to")
    parser.add_argument("--low-threshold", type=int, default=50, help="Canny lower threshold")
    parser.add_argument("--high-threshold", type=int, default=150, help="Canny upper threshold")
    parser.add_argument(
        "--dilate", type=int, default=1,
        help="Dilation passes to thicken edge lines so they survive resizing (0 to disable)",
    )
    parser.add_argument(
        "--invert", action="store_true",
        help="Use black edges on a white background",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Only process the first N images — useful for previewing threshold settings",
    )
    args = parser.parse_args()

    in_dir = Path(args.input)
    out_dir = Path(args.output)

    if not in_dir.exists():
        sys.exit(f"Input folder not found: {in_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(f for f in in_dir.iterdir() if f.suffix.lower() in VALID_EXTS)
    if not files:
        sys.exit(f"No images found in {in_dir}")

    if args.limit:
        files = files[: args.limit]

    print(f"Generating edge maps for {len(files)} image(s): {in_dir} -> {out_dir}")
    written = 0
    for f in files:
        edges = generate_edge_map(
            f, args.low_threshold, args.high_threshold, args.dilate, invert=args.invert
        )
        if edges is None:
            print(f"  skipped (couldn't read): {f.name}")
            continue
        cv2.imwrite(str(out_dir / f.name), edges)
        written += 1

    print(f"Done. Wrote {written} edge map(s) to {out_dir}")
    if args.limit:
        print("(This was a limited preview run — drop --limit to process the full folder.)")


if __name__ == "__main__":
    main()
