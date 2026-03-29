import os

WIDTH = 1000
HEIGHT = 1000

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <defs>
    <style>
      .text {{ fill: #FFFDD0; font-family: 'Garamond', 'EB Garamond', 'Times New Roman', serif; }}
      .accent {{ fill: #F05E39; }}
      .achacks-text {{ font-size: 200px; }}
      .year {{ 
        font-family: 'Georgia', serif;
        font-size: 90px;  
        letter-spacing: 2px; 
      }}
    </style>
  </defs>

  <!-- Title Block -->
  <g transform="translate(180, 500)">
    <!-- J Logo -->
    <g transform="translate(-25, -190) scale(0.28)">
      <path d="M 681.89,42.24 A 8.00,8.00 0 0,1 694.00,49.11 L 694.00,590.45 A 82.00,82.00 0 0,1 652.73,661.62 L 382.87,816.06 A 28.00,28.00 0 0,1 355.11,816.09 L 85.43,662.59 A 82.00,82.00 0 0,1 44.00,591.32 L 44.00,438.48 A 45.00,45.00 0 0,1 67.15,399.14 L 149.11,353.60 A 8.00,8.00 0 0,1 161.00,360.60 L 161.00,538.50 A 58.00,58.00 0 0,0 190.02,588.74 L 356.51,684.79 A 25.00,25.00 0 0,0 381.49,684.79 L 547.98,588.74 A 58.00,58.00 0 0,0 577.00,538.50 L 577.00,130.52 A 45.00,45.00 0 0,1 598.90,91.90 Z" fill="#F05E39" />
    </g>
    <!-- achacks text -->
    <text class="text achacks-text" x="180" y="-10">achacks</text>
    <!-- 2026 text -->
    <text class="accent year" x="190" y="90">2026</text>
  </g>
</svg>"""

def main():
    svg_content = SVG_TEMPLATE.format(width=WIDTH, height=HEIGHT)
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "tshirt_front.svg")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()
