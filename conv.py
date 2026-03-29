import os
from playwright.sync_api import sync_playwright

def convert_svg_to_transparent_png(svg_path, png_path):
    # Make sure the output directory exists
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    
    # Read your SVG file
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    # Wrap the SVG in a tiny HTML document with a transparent background
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 0; background: transparent; }}
            svg {{ display: block; }}
        </style>
    </head>
    <body>
        {svg_content}
    </body>
    </html>
    """

    with sync_playwright() as p:
        # Launch headless Chromium
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Load the HTML wrapping our SVG
        page.set_content(html_content)
        
        # Target just the SVG element itself
        svg_element = page.locator('svg')
        
        # Take a screenshot with omit_background=True to keep it transparent
        svg_element.screenshot(path=png_path, omit_background=True)
        
        browser.close()
        print(f"Successfully saved perfect transparent PNG to {png_path}")

def main():
    input_path = "output/tshirt_front.svg"
    output_path = "output/tshirt_front.png"
    
    try:
        convert_svg_to_transparent_png(input_path, output_path)
    except Exception as e:
        print(f"Error during conversion: {e}")

if __name__ == "__main__":
    main()