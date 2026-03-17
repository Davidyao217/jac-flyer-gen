import os

WIDTH = 1000
HEIGHT = 1000

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      .bg {{ fill: #221212; }}
      .text {{ fill: #FFFDD0; font-family: 'Garamond', 'EB Garamond', 'Times New Roman', serif; }}
      .accent {{ fill: #FF5E00; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 800; }}
      .location {{ font-size: 24px; letter-spacing: 4px; opacity: 0.7; text-transform: uppercase; }}
      .j-logo {{ font-size: 380px; letter-spacing: -10px; }}
      .ac-text {{ font-size: 200px; }}
      .hacks-text {{ font-size: 200px; }}
      .dates {{ font-size: 70px; letter-spacing: 2px; }}
      .cta-text {{ font-family: 'SF Mono', Consolas, 'Courier New', monospace; font-size: 34px; font-weight: normal; }}
      .sponsors-list {{ font-size: 28px; letter-spacing: 2px; opacity: 0.8; text-transform: uppercase; }}
      .line {{ stroke: #FFFDD0; stroke-width: 2; opacity: 0.6; }}
      .building {{ stroke: #F05E39; stroke-width: 1.5; fill: none; opacity: 0.5; stroke-linecap: round; stroke-linejoin: round; }}
    </style>
    <filter id="creamTint" color-interpolation-filters="sRGB">
      <feColorMatrix type="matrix" values="
        0 0 0 0 1.0
        0 0 0 0 0.992
        0 0 0 0 0.816
        -0.2126 -0.7152 -0.0722 1 0" />
    </filter>
  </defs>

  <!-- Background -->
  <rect class="bg" width="{width}" height="{height}" />

  <!-- Background Building Line Art -->
  <g transform="translate(0, 0) scale(0.65)" class="building">
    {building_paths}
  </g>

  <!-- Location -->
  <text class="text location" x="920" y="80" text-anchor="end">ANN ARBOR</text>

  <!-- Title Block -->
  <g transform="translate(5, -35) scale(1.1)">
    <!-- "J" and "ac" -->
    <g transform="translate(80, 140) scale(0.25)">
      <path d="M 681.89,42.24 A 8.00,8.00 0 0,1 694.00,49.11 L 694.00,590.45 A 82.00,82.00 0 0,1 652.73,661.62 L 382.87,816.06 A 28.00,28.00 0 0,1 355.11,816.09 L 85.43,662.59 A 82.00,82.00 0 0,1 44.00,591.32 L 44.00,438.48 A 45.00,45.00 0 0,1 67.15,399.14 L 149.11,353.60 A 8.00,8.00 0 0,1 161.00,360.60 L 161.00,538.50 A 58.00,58.00 0 0,0 190.02,588.74 L 356.51,684.79 A 25.00,25.00 0 0,0 381.49,684.79 L 547.98,588.74 A 58.00,58.00 0 0,0 577.00,538.50 L 577.00,130.52 A 45.00,45.00 0 0,1 598.90,91.90 Z" fill="#F05E39" />
    </g>
    <g transform="translate(30, 40) skewX(-10) translate(40, 0)">
      <text class="text ac-text" x="240" y="260">ac</text>
      <text class="text hacks-text" x="270" y="440">Hacks</text>
      <text class="text dates" x="390" y="540">April 4-5th</text>
    </g>
  </g>

  <!-- Call to Action Divider -->
  <text class="cta-text" fill="#FFFDD0" x="120" y="700">
    <tspan x="120" dy="0">def <tspan fill="#F05E39" font-weight="bold">apply_now</tspan>(</tspan>
    <tspan x="180" dy="50">link: str = "<tspan fill="#F05E39" font-weight="bold">bit.ly/4s064JH</tspan>"</tspan>
    <tspan x="120" dy="50">) -&gt; GoodTimesAndEmployment by llm();</tspan>
  </text>

  <!-- Sponsors -->
  <text class="text location" x="960" y="900" text-anchor="end" style="font-size: 28px;">SPONSORS:</text>
  {sponsors_logos}
  
  <!-- Guide Line -->
  <line x1="0" y1="{guide_y}" x2="{width}" y2="{guide_y}" stroke="white" stroke-width="2" stroke-dasharray="5,5" opacity="0.0" />
</svg>"""

import re
import base64

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
    
    # Extract path elements, handling newlines and other attributes that tools like Inkscape add
    # The \s+ prevents matching 'id=' as 'd='
    d_values = re.findall(r'<path[^>]*\s+d="([^"]+)"', content)
    paths = [f'<path d="{d}" />' for d in d_values]
    building_paths_str = "\n    ".join(paths)

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
    x_positions = [123, 345, 566, 788]
        
    sponsor_tags = []
    for i, sponsor in enumerate(sponsors):
        filepath = os.path.join(os.path.dirname(__file__), sponsor)
        uri = get_image_data_uri(filepath)
        x = x_positions[i]
        y = y_positions[i]
        scale = scales[i]
        # Using <image> base64 embed directly into the SVG
        sponsor_tags.append(f'<image x="{x:.1f}" y="{y}" width="{140 * scale}" height="{70 * scale}" preserveAspectRatio="xMidYMid meet" href="{uri}" filter="url(#creamTint)" />')
        
    sponsors_str = "\n  ".join(sponsor_tags)
    
    guide_y = 947  # Adjust this value to move the horizontal line
    
    svg_content = SVG_TEMPLATE.format(
        width=WIDTH, 
        height=HEIGHT, 
        building_paths=building_paths_str, 
        sponsors_logos=sponsors_str,
        guide_y=guide_y
    )
    output_path = os.path.join(os.path.dirname(__file__), "square_flyer.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()
