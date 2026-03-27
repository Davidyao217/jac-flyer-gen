import os
import re
import base64

WIDTH = 1000
HEIGHT = 1000

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      .text {{ fill: #1C1008; font-family: 'Garamond', 'EB Garamond', 'Times New Roman', serif; }}
      .accent {{ fill: #FF5E00; }}
      .j-logo {{ font-size: 380px; letter-spacing: -10px; }}
      .ac-text {{ font-size: 200px; font-weight: 500;}}
      .hacks-text {{ font-size: 200px; font-weight: 500;}}
    </style>
    <filter id="darkTint" color-interpolation-filters="sRGB">
      <feColorMatrix type="matrix" values="
        0 0 0 0 0.110
        0 0 0 0 0.063
        0 0 0 0 0.031
        -0.2126 -0.7152 -0.0722 1 0" />
    </filter>
  </defs>

  <!-- NO background rect — fully transparent -->

  <!-- Title Block — centred on canvas -->
  <g transform="translate(5, 100) scale(1.1)">
    <!-- "J" logo -->
    <g transform="translate(80, 140) scale(0.25)">
      <path d="M 681.89,42.24 A 8.00,8.00 0 0,1 694.00,49.11 L 694.00,590.45 A 82.00,82.00 0 0,1 652.73,661.62 L 382.87,816.06 A 28.00,28.00 0 0,1 355.11,816.09 L 85.43,662.59 A 82.00,82.00 0 0,1 44.00,591.32 L 44.00,438.48 A 45.00,45.00 0 0,1 67.15,399.14 L 149.11,353.60 A 8.00,8.00 0 0,1 161.00,360.60 L 161.00,538.50 A 58.00,58.00 0 0,0 190.02,588.74 L 356.51,684.79 A 25.00,25.00 0 0,0 381.49,684.79 L 547.98,588.74 A 58.00,58.00 0 0,0 577.00,538.50 L 577.00,130.52 A 45.00,45.00 0 0,1 598.90,91.90 Z" fill="#FF5E00" />
    </g>
    <!-- "ac" and "Hacks" -->
    <g transform="translate(30, 40) skewX(-10) translate(40, 0)">
      <text class="text ac-text" x="240" y="260">ac</text>
      <text class="text hacks-text" x="270" y="440">Hacks</text>
    </g>
  </g>

  <!-- Year "2026" -->
  <text x="550" y="800" style="font-family: 'Arial Black', 'Impact', 'Helvetica', sans-serif; font-size: 90px; font-weight: 900; fill: #1C1008;">2026</text>

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
    # Sponsor logos
    sponsors = [
        "clean_assets/jaseci_logo.svg",
        "clean_assets/michigan_block.svg",
        "clean_assets/nvidia_logo.svg",
        "clean_assets/nsf_logo.svg"
    ]
    scales = [1.0, 0.8, 1.4, 1.5]
    total_scale = 0.8
    scales = [scale * total_scale for scale in scales]

    y_positions = [920, 923, 910, 905]
    x_positions = [113, 335, 556, 778]

    sponsor_tags = []
    for i, sponsor in enumerate(sponsors):
        filepath = os.path.join(os.path.dirname(__file__), sponsor)
        uri = get_image_data_uri(filepath)
        x = x_positions[i]
        y = y_positions[i]
        scale = scales[i]
        sponsor_tags.append(
            f'<image x="{x:.1f}" y="{y}" width="{140 * scale}" height="{70 * scale}" '
            f'preserveAspectRatio="xMidYMid meet" href="{uri}" filter="url(#darkTint)" />'
        )

    sponsors_str = "\n  ".join(sponsor_tags)

    svg_content = SVG_TEMPLATE.format(
        width=WIDTH,
        height=HEIGHT,
        sponsors_logos=sponsors_str,
    )
    output_path = os.path.join(os.path.dirname(__file__), "tshirt_graphic.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_path}")


if __name__ == "__main__":
    main()
