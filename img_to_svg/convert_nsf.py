import os
import base64

def convert_nsf_to_svg(input_path, output_path):
    """
    Convert the NSF logo from WebP to SVG by embedding the raster image
    as a base64-encoded <image> element inside an SVG wrapper.

    The NSF logo has complex gradients (blue globe, gold gear, white text
    with drop shadows) that cannot be faithfully reproduced via contour
    tracing. Embedding preserves full visual fidelity while producing a
    valid SVG file that can be used alongside the other sponsor logos.
    """
    with open(input_path, 'rb') as f:
        data = f.read()

    b64 = base64.b64encode(data).decode('utf-8')

    # Determine mime type from extension
    ext = os.path.splitext(input_path)[1].lower()
    mime_map = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}
    mime = mime_map.get(ext, 'image/webp')

    # Use a square viewBox matching the image aspect (NSF logo is ~1:1)
    # We'll use a generic 100x100 viewBox so it scales cleanly
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 100 100" width="100" height="100">
  <image width="100" height="100" preserveAspectRatio="xMidYMid meet"
         href="data:{mime};base64,{b64}" />
</svg>'''

    with open(output_path, 'w') as f:
        f.write(svg_content)

    print(f"Success! NSF logo saved to: {output_path}")

convert_nsf_to_svg("img_to_svg/nsf.webp", "clean_assets/nsf_logo.svg")
