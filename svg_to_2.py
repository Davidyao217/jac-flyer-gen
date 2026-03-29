#!/usr/bin/env python3
"""
svg_to_2color.py — Flatten a full-color SVG to exactly 2 colors.

Usage:
    python svg_to_2color.py input.svg output.svg [--fg "#000000"] [--bg "#ffffff"] [--threshold 128]

Options:
    --fg          Foreground (dark) color  [default: #000000]
    --bg          Background (light) color [default: #ffffff]
    --threshold   0–255 luminance cutoff. Pixels darker than this become FG, lighter become BG [default: 128]
    --dpi         Rasterization resolution (higher = more detail preserved) [default: 300]

Requirements:
    pip install cairosvg Pillow
"""

import argparse
import sys
import os


def check_dependencies():
    missing = []
    try:
        import cairosvg
    except ImportError:
        missing.append("cairosvg")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    if missing:
        print(f"Missing dependencies. Install with:\n  pip install {' '.join(missing)}")
        sys.exit(1)


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_luminance(r, g, b) -> float:
    """Perceived luminance (0–255)."""
    return 0.299 * r + 0.587 * g + 0.114 * b


def rasterize_svg(svg_path: str, dpi: int) -> "Image.Image":
    import cairosvg
    from PIL import Image
    import io

    png_bytes = cairosvg.svg2png(url=svg_path, dpi=dpi)
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    return img


def flatten_to_2color(img: "Image.Image", fg_hex: str, bg_hex: str, threshold: int) -> "Image.Image":
    from PIL import Image

    fg_rgb = hex_to_rgb(fg_hex)
    bg_rgb = hex_to_rgb(bg_hex)

    rgba = img.load()
    width, height = img.size
    result = Image.new("RGBA", (width, height))
    out = result.load()

    for y in range(height):
        for x in range(width):
            r, g, b, a = rgba[x, y]

            # Fully transparent pixels → background
            if a < 10:
                out[x, y] = (*bg_rgb, 255)
                continue

            # Blend pixel against white background to account for transparency
            alpha = a / 255.0
            blended_r = int(r * alpha + 255 * (1 - alpha))
            blended_g = int(g * alpha + 255 * (1 - alpha))
            blended_b = int(b * alpha + 255 * (1 - alpha))

            lum = rgb_luminance(blended_r, blended_g, blended_b)

            if lum < threshold:
                out[x, y] = (*fg_rgb, 255)
            else:
                out[x, y] = (*bg_rgb, 255)

    return result


def image_to_svg(img: "Image.Image", output_path: str):
    """
    Convert the 2-color PIL image to an SVG using base64-embedded PNG.
    Keeps it as a single clean SVG file.
    """
    from PIL import Image
    import base64
    import io

    width, height = img.size

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    png_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <image width="{width}" height="{height}"
         xlink:href="data:image/png;base64,{png_b64}"/>
</svg>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def main():
    parser = argparse.ArgumentParser(
        description="Flatten a full-color SVG to exactly 2 colors for t-shirt printing."
    )
    parser.add_argument("input",  help="Path to the input SVG file")
    parser.add_argument("output", help="Path for the output SVG file")
    parser.add_argument("--fg",        default="#000000", help="Foreground color hex (default: #000000)")
    parser.add_argument("--bg",        default="#ffffff", help="Background color hex (default: #ffffff)")
    parser.add_argument("--threshold", type=int, default=128,
                        help="Luminance threshold 0–255 (default: 128). Lower = more goes to FG.")
    parser.add_argument("--dpi",       type=int, default=300,
                        help="Rasterization DPI — higher preserves more detail (default: 300)")

    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"Error: input file not found: {args.input}")
        sys.exit(1)

    if not (0 <= args.threshold <= 255):
        print("Error: --threshold must be between 0 and 255")
        sys.exit(1)

    check_dependencies()

    print(f"Rasterizing SVG at {args.dpi} DPI...")
    img = rasterize_svg(args.input, args.dpi)
    print(f"  → Image size: {img.size[0]}×{img.size[1]} px")

    print(f"Flattening to 2 colors: FG={args.fg}  BG={args.bg}  threshold={args.threshold}...")
    flat = flatten_to_2color(img, args.fg, args.bg, args.threshold)

    print(f"Writing output SVG: {args.output}")
    image_to_svg(flat, args.output)

    print("Done! ✓")
    print(f"\nTip: If the result has too much or too little detail, adjust --threshold")
    print(f"     Lower  threshold (e.g. 80)  → only very dark areas become FG")
    print(f"     Higher threshold (e.g. 180) → more of the image becomes FG")


if __name__ == "__main__":
    main()