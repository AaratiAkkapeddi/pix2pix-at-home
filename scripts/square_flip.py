#!/usr/bin/env python3
"""
Crop images to centered squares and optionally create flipped copies.

Example:
    python scripts/square_flip.py --input data/B --output data/A --limit 10 --flip
"""

import argparse
import sys
from pathlib import Path

try:
    import cv2
except ImportError:
    sys.exit("Install OpenCV with: pip install opencv-python-headless")


VALID_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def crop_to_square(image):
    height, width = image.shape[:2]
    size = min(height, width)
    top = (height - size) // 2
    left = (width - size) // 2
    return image[top:top + size, left:left + size]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Input image folder")
    parser.add_argument("--output", required=True, help="Output image folder")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--flip",
        action="store_true",
        help="Also save a horizontally flipped copy of each image",
    )
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.is_dir():
        sys.exit(f"Input folder not found: {input_dir}")

    files = sorted(
        file for file in input_dir.iterdir()
        if file.is_file() and file.suffix.lower() in VALID_EXTS
    )

    if args.limit is not None:
        files = files[:args.limit]

    if not files:
        sys.exit(f"No images found in {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    written = 0

    for image_path in files:
        image = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

        if image is None:
            print(f"Skipped unreadable image: {image_path.name}")
            continue

        cropped = crop_to_square(image)

        # Save the original cropped image.
        cv2.imwrite(str(output_dir / image_path.name), cropped)
        written += 1

        # Save a separate flipped copy.
        if args.flip:
            flipped_name = f"{image_path.stem}_flipped{image_path.suffix}"
            flipped = cv2.flip(cropped, 1)
            cv2.imwrite(str(output_dir / flipped_name), flipped)
            written += 1

    print(f"Wrote {written} image(s) to {output_dir}")


if __name__ == "__main__":
    main()