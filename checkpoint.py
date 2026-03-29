import os
import re
import base64
import math

WIDTH = 1000
HEIGHT = 1150

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      .text {{ fill: #FFFDD0; font-family: 'Garamond', 'EB Garamond', 'Times New Roman', serif; }}
      .accent {{ fill: #F05E39; }}
      .j-logo {{ font-size: 380px; letter-spacing: -10px; }}
      .ac-text {{ font-size: 200px; font-weight: 500;}}
      .hacks-text {{ font-size: 200px; font-weight: 500;}}
      .building {{ stroke: #F05E39; stroke-width: 3; fill: none; opacity: 1; stroke-linecap: round; stroke-linejoin: round; }}
    </style>
    <filter id="creamTint" color-interpolation-filters="sRGB">
      <feColorMatrix type="matrix" values="
        0 0 0 0 1.000
        0 0 0 0 0.992
        0 0 0 0 0.816
        0 0 0 1 0" />
    </filter>
  </defs>

  <rect fill="#221212" width="{width}" height="{height}" />

  <!-- Background Building Line Art (thicker strokes for screen printing) -->
  <g transform="translate(100, 0) scale(0.65)" class="building">
    {building_paths}
  </g>

  <!-- Title Block — centred on canvas -->
  <g transform="translate(70, 3) scale(0.95)">
    <!-- "J" logo -->
    <g transform="translate(80, 140) scale(0.25)">
      <path d="M 681.89,42.24 A 8.00,8.00 0 0,1 694.00,49.11 L 694.00,590.45 A 82.00,82.00 0 0,1 652.73,661.62 L 382.87,816.06 A 28.00,28.00 0 0,1 355.11,816.09 L 85.43,662.59 A 82.00,82.00 0 0,1 44.00,591.32 L 44.00,438.48 A 45.00,45.00 0 0,1 67.15,399.14 L 149.11,353.60 A 8.00,8.00 0 0,1 161.00,360.60 L 161.00,538.50 A 58.00,58.00 0 0,0 190.02,588.74 L 356.51,684.79 A 25.00,25.00 0 0,0 381.49,684.79 L 547.98,588.74 A 58.00,58.00 0 0,0 577.00,538.50 L 577.00,130.52 A 45.00,45.00 0 0,1 598.90,91.90 Z" fill="#F05E39" />
    </g>
    <!-- "ac" and "Hacks" -->
    <g transform="translate(30, 40) skewX(-10) translate(40, 0)">
      <text class="text ac-text" x="240" y="260">ac</text>
      <text class="text hacks-text" x="270" y="440">Hacks</text>
    </g>
  </g>

  <!-- Sponsors -->
  {sponsors_logos}
</svg>"""


def get_image_data_uri(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.svg':
        mime = 'image/svg+xml'
    elif ext in ['.jpg', '.jpeg']:
        mime = 'image/jpeg'
    else:
        mime = 'image/png'
    b64 = base64.b64encode(data).decode('utf-8')
    return f"data:{mime};base64,{b64}"


def main():
    building_path = os.path.join(os.path.dirname(__file__), "clean_assets/clean_vector.svg")
    with open(building_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract path elements
    d_values = re.findall(r'<path[^>]*\s+d="([^"]+)"', content)
    paths = [f'<path d="{d}" />' for d in d_values]
    building_paths_str = "\n    ".join(paths)

    sponsors = [
        "clean_assets/jaseci_logo.svg",
        "clean_assets/lovable-logo-icon.svg",
        "clean_assets/Anthropic_logo.svg",
        "clean_assets/michigan_block.svg",
        "clean_assets/nvidia_logo.svg",
        "clean_assets/nsf_bw-removebg-preview.png",
        "clean_assets/backboard.png",
        "clean_assets/monster.png",
        "clean_assets/wip.png",
        "clean_assets/base44.png",
        "clean_assets/insforge.svg",
        "clean_assets/mastra.svg",
        "clean_assets/mdst.png",
        "clean_assets/ship.svg",
    ]
    
    # Scaling settings
    scales = [1.0, 0.8, 1.4, 1.5]
    total_scale = 0.8
    base_width = 140
    base_height = 70

    # Grid Settings
    GRID_START_X = 50   # Top-left corner X of the entire grid
    GRID_START_Y = 600  # Top-left corner Y of the entire grid
    CELL_WIDTH = 180    # Horizontal space allocated per logo
    CELL_HEIGHT = 100   # Vertical space allocated per logo

    # Determine optimal grid size (nxn)
    num_logos = len(sponsors)
    n = math.ceil(math.sqrt(num_logos))

    sponsor_tags = []
    for i, sponsor in enumerate(sponsors):
        filepath = os.path.join(os.path.dirname(__file__), sponsor)
        uri = get_image_data_uri(filepath)
        
        # Calculate grid position
        row = i // n
        col = i % n
        
        x = GRID_START_X + (col * CELL_WIDTH)
        y = GRID_START_Y + (row * CELL_HEIGHT)
        
        # Apply scale safely (fallback to 1.0 if more logos than scales are added)
        current_scale = (scales[i] if i < len(scales) else 1.0) * total_scale
        img_w = base_width * current_scale
        img_h = base_height * current_scale

        sponsor_tags.append(
            f'<image x="{x:.1f}" y="{y:.1f}" width="{img_w:.1f}" height="{img_h:.1f}" '
            f'preserveAspectRatio="xMidYMid meet" href="{uri}" filter="url(#creamTint)" />'
        )

    sponsors_str = "\n  ".join(sponsor_tags)

    svg_content = SVG_TEMPLATE.format(
        width=WIDTH,
        height=HEIGHT,
        building_paths=building_paths_str,
        sponsors_logos=sponsors_str,
    )
    output_path = os.path.join(os.path.dirname(__file__), "tshirt_graphic.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_path}")


if __name__ == "__main__":
    main()