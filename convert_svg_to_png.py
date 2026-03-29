from playwright.sync_api import sync_playwright
import os
import urllib.parse
import math

def convert_svg_high_res(input_svg, output_file, format_type='png', scale_factor=4):
    if not os.path.exists(input_svg):
        print(f"Error: Could not find '{input_svg}'")
        return

    abs_path = os.path.abspath(input_svg)
    file_url = f"file://{urllib.parse.quote(abs_path)}"
    format_type = format_type.lower()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(device_scale_factor=scale_factor)
        page = context.new_page()
        
        page.goto(file_url)
        page.wait_for_load_state('networkidle')

        # Safely handle the DOM depending on how Chromium loaded the SVG
        page.evaluate('''() => {
            if (document.body) {
                document.body.style.margin = '0';
                document.body.style.padding = '0';
            }
            const svg = document.querySelector('svg') || document.documentElement;
            if (svg && svg.tagName.toLowerCase() === 'svg') {
                svg.style.display = 'block'; 
                if (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width > 0) {
                    svg.style.width = svg.viewBox.baseVal.width + 'px';
                    svg.style.height = svg.viewBox.baseVal.height + 'px';
                }
            }
        }''')

        # Locate the SVG, even if it's the root element
        svg_element = page.locator('svg').first
        
        if format_type == 'pdf':
            box = svg_element.bounding_box()
            width = f"{math.ceil(box['width'])}px"
            height = f"{math.ceil(box['height'])}px"
            page.pdf(path=output_file, width=width, height=height, print_background=True)
            print(f"Success! Exact-size PDF created: {output_file}")
            
        elif format_type == 'png':
            svg_element.screenshot(path=output_file, omit_background=True)
            
            try:
                from PIL import Image
                with Image.open(output_file) as img:
                    bbox = img.getbbox()
                    if bbox:
                        cropped_img = img.crop(bbox)
                        cropped_img.save(output_file)
                        print(f"Success! High-res, tightly cropped PNG created: {output_file}")
                    else:
                        print(f"Saved {output_file}, but it appears completely transparent.")
            except ImportError:
                print(f"Saved {output_file}. (Pillow not installed, auto-crop skipped).")
            
        elif format_type in ['jpg', 'jpeg']:
            if page.evaluate('!!document.body'):
                page.evaluate('document.body.style.background = "white"')
            svg_element.screenshot(path=output_file, type='jpeg', quality=100)
            print(f"Success! High-res JPEG created at {scale_factor}x scale: {output_file}")
            
        else:
            print("Unsupported format. Please choose 'pdf', 'png', or 'jpeg'.")

        browser.close()

# ==========================================
# Run the conversion:
# ==========================================
convert_svg_high_res('output/tshirt_graphic_back.svg', 'output/tshirt_graphic_back_jac_cream_no_skew.png', 'png', scale_factor=4)