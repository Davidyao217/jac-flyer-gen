import re

def hex_to_rgb(hex_color):
    """Convert hex string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    if len(hex_color) != 6:
        return (0, 0, 0)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_str_to_rgb(rgb_str):
    """Extract RGB values from rgb() or rgba() strings."""
    numbers = re.findall(r'\d+', rgb_str)
    if len(numbers) >= 3:
        return tuple(int(n) for n in numbers[:3])
    return (0, 0, 0)

def get_brightness(rgb):
    """Calculate perceived brightness (0-255)."""
    return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

def flatten_svg_aggressively(input_file, output_file, dark_color="#000000", light_color="#FFFFFF", threshold=128):
    """Hunt down and replace all color values in the SVG text."""
    with open(input_file, 'r', encoding='utf-8') as f:
        svg_content = f.read()

    def replacer(match):
        color_str = match.group(0)
        if color_str.startswith('#'):
            rgb = hex_to_rgb(color_str)
        elif color_str.startswith('rgb'):
            rgb = rgb_str_to_rgb(color_str)
        else:
            return color_str
        
        brightness = get_brightness(rgb)
        return light_color if brightness > threshold else dark_color

    # 1. Replace all hex codes (#FFF or #FFFFFF)
    svg_content = re.sub(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', replacer, svg_content)
    
    # 2. Replace all rgb() and rgba() strings
    svg_content = re.sub(r'rgba?\([^)]+\)', replacer, svg_content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
        
    print(f"Aggressively flattened SVG saved to {output_file}")

# --- Run the Script ---
if __name__ == "__main__":
    INPUT_SVG = 'clean_assets/nsf_logo.svg'
    OUTPUT_SVG = 'clean_assets/nsf_logo_2color.svg'
    
    # Define your two T-shirt colors here
    DARK_HEX = '#004C97' 
    LIGHT_HEX = '#FFFFFF'
    
    flatten_svg_aggressively(INPUT_SVG, OUTPUT_SVG, dark_color=DARK_HEX, light_color=LIGHT_HEX)