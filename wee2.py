#!/usr/bin/env python3
"""
logo_to_svg.py - Convert a logo image to a clean SVG with background removed.

Usage:
    python logo_to_svg.py input.png output.svg [--color "#FFCC00"] [--threshold 80]

Arguments:
    input.png     Path to the input image (PNG, JPG, etc.)
    output.svg    Path for the output SVG file
    --color       Hex color for the logo shape (default: auto-detected from image)
    --threshold   Brightness threshold 0-255 to separate logo from background (default: 80)
    --bg-dark     Hint that background is dark (auto-detected if omitted)
"""

import argparse
import subprocess
import sys
import os
import tempfile
import re
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("Error: Pillow and numpy are required. Install with:\n  pip install Pillow numpy")
    sys.exit(1)


def detect_dominant_logo_color(img_array, bg_is_dark=True):
    """Detect the dominant non-background color in the image."""
    # Flatten pixels
    pixels = img_array.reshape(-1, img_array.shape[2])

    if bg_is_dark:
        # Background is dark → logo pixels are bright
        brightness = pixels.mean(axis=1)
        logo_pixels = pixels[brightness > 80]
    else:
        # Background is light → logo pixels are dark
        brightness = pixels.mean(axis=1)
        logo_pixels = pixels[brightness < 180]

    if len(logo_pixels) == 0:
        return "#FFFFFF" if bg_is_dark else "#000000"

    # Median color of logo pixels
    median = np.median(logo_pixels, axis=0).astype(int)
    return "#{:02X}{:02X}{:02X}".format(median[0], median[1], median[2])


def detect_background(img_array):
    """Detect whether the background is dark or light by sampling corners."""
    h, w = img_array.shape[:2]
    corner_size = max(10, min(h, w) // 20)
    corners = [
        img_array[:corner_size, :corner_size],
        img_array[:corner_size, -corner_size:],
        img_array[-corner_size:, :corner_size],
        img_array[-corner_size:, -corner_size:],
    ]
    corner_pixels = np.concatenate([c.reshape(-1, img_array.shape[2]) for c in corners])
    avg_brightness = corner_pixels.mean()
    return avg_brightness < 128  # True = dark background


def image_to_binary_bmp(img_array, threshold, bg_is_dark):
    """Convert image to binary (black/white) based on threshold."""
    # Convert to grayscale luminance
    if img_array.shape[2] == 4:
        rgb = img_array[:, :, :3]
        alpha = img_array[:, :, 3]
    else:
        rgb = img_array
        alpha = None

    gray = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]

    if bg_is_dark:
        # Logo is bright → white in binary image
        binary = (gray > threshold).astype(np.uint8) * 255
    else:
        # Logo is dark → invert so logo becomes white
        binary = (gray <= threshold).astype(np.uint8) * 255

    # If alpha channel exists, mask out transparent regions
    if alpha is not None:
        binary[alpha < 128] = 0

    return binary


def rasterize_to_bmp(binary_array, tmp_bmp_path):
    """Save binary array as BMP for potrace."""
    img = Image.fromarray(binary_array, mode='L')
    # Convert to pure black/white 1-bit
    img = img.convert('1')
    img.save(tmp_bmp_path, format='BMP')


def trace_with_potrace(bmp_path, svg_path, color):
    """Run potrace to convert BMP to SVG."""
    # Check potrace is available
    result = subprocess.run(['which', 'potrace'], capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "potrace is not installed. Install it with:\n"
            "  Ubuntu/Debian: sudo apt-get install potrace\n"
            "  macOS:         brew install potrace\n"
            "  Windows:       https://potrace.sourceforge.net/"
        )

    # Parse color for potrace (it wants hex without #)
    hex_color = color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255

    cmd = [
        'potrace',
        '--svg',
        '--output', svg_path,
        '--color', color,
        '--turdsize', '5',      # Remove tiny noise specks
        '--alphamax', '1.0',    # Smooth corners
        '--opttolerance', '0.2',# Curve optimization
        bmp_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"potrace failed:\n{result.stderr}")


def clean_svg(svg_path, color):
    """Post-process SVG: remove potrace's background path, set viewBox cleanly."""
    with open(svg_path, 'r') as f:
        content = f.read()

    # Potrace always emits the first path as a full-canvas background rectangle
    # in the form: M0 <height> l0 -<height> <width> 0 <width> 0 0 <height> ...
    # Strip it so the SVG has a transparent background.
    content = re.sub(
        r'<path[^d]*d="M0 \d[\d.]* l0 -\d[\d.]* \d[\d.]* 0 \d[\d.]* 0[^"]*"[^/]*/?>',
        '',
        content
    )
    # Remove any <rect> background elements
    content = re.sub(
        r'<rect[^>]*/?>',
        '',
        content
    )
    # Remove any explicit background fill/style on the <svg> tag
    content = re.sub(r'(style="[^"]*?)background[^;"]*;?', r'\1', content)

    with open(svg_path, 'w') as f:
        f.write(content)


def convert_logo(input_path, output_path, color=None, threshold=80, bg_dark=None):
    """Main conversion pipeline."""
    print(f"Loading image: {input_path}")
    img = Image.open(input_path)

    # Ensure RGB or RGBA
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')

    arr = np.array(img)
    if arr.shape[2] == 3:
        # Add alpha channel (fully opaque) for uniform processing
        alpha = np.full(arr.shape[:2], 255, dtype=np.uint8)
        arr = np.dstack([arr, alpha])

    # Auto-detect background
    if bg_dark is None:
        bg_dark = detect_background(arr[:, :, :3])
        print(f"Detected {'dark' if bg_dark else 'light'} background")

    # Auto-detect color
    if color is None:
        color = detect_dominant_logo_color(arr[:, :, :3], bg_is_dark=bg_dark)
        print(f"Detected logo color: {color}")
    else:
        print(f"Using specified color: {color}")

    # Create binary mask
    print(f"Applying threshold: {threshold}")
    binary = image_to_binary_bmp(arr, threshold, bg_dark)

    # Write to temp BMP
    with tempfile.TemporaryDirectory() as tmpdir:
        bmp_path = os.path.join(tmpdir, 'logo.bmp')
        rasterize_to_bmp(binary, bmp_path)

        # Trace with potrace
        svg_tmp = os.path.join(tmpdir, 'logo.svg')
        print("Tracing with potrace...")
        trace_with_potrace(bmp_path, svg_tmp, color)

        # Clean up SVG
        clean_svg(svg_tmp, color)

        # Copy to output
        import shutil
        shutil.copy(svg_tmp, output_path)

    print(f"✓ SVG saved to: {output_path}")
    print(f"  Color: {color}")

    # Report file sizes
    in_size = Path(input_path).stat().st_size
    out_size = Path(output_path).stat().st_size
    print(f"  Input:  {in_size:,} bytes ({Path(input_path).suffix})")
    print(f"  Output: {out_size:,} bytes (.svg)")


def main():
    parser = argparse.ArgumentParser(
        description='Convert a logo image to an SVG with background removed.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('input', help='Input image path (PNG, JPG, etc.)')
    parser.add_argument('output', help='Output SVG path')
    parser.add_argument(
        '--color',
        default=None,
        help='Hex color for logo shape, e.g. "#FFD700" (default: auto-detected)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=80,
        help='Brightness threshold 0-255 to separate logo from background (default: 80). '
             'Lower = less of the image counted as logo. Raise if logo is faint.'
    )
    parser.add_argument(
        '--bg-dark',
        action='store_true',
        default=None,
        help='Force treatment of background as dark (auto-detected by default)'
    )
    parser.add_argument(
        '--bg-light',
        action='store_true',
        help='Force treatment of background as light'
    )

    args = parser.parse_args()

    # Resolve bg_dark
    bg_dark = None
    if args.bg_dark:
        bg_dark = True
    elif args.bg_light:
        bg_dark = False

    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    try:
        convert_logo(
            input_path=args.input,
            output_path=args.output,
            color=args.color,
            threshold=args.threshold,
            bg_dark=bg_dark,
        )
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()