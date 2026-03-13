import cv2
import numpy as np

def extract_solid_logo(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    # 1. Stronger blur to remove craggy JPEG noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
        
    # 2. Simple Otsu threshold since it's likely a dark background or dark text on light background
    # We want the logo to be white (255) for findContours. Let's check polarity.
    # The logo has some bright text/shapes on a dark background?
    # Earlier we found pixels > 127: 902, <= 127: 39098. 
    # So it's mostly dark, the logo is bright.
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    # 3. Find contours
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    height, width = img.shape
    svg_elements = []
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')

    path_data = []
    
    for cnt in contours:
        if cv2.contourArea(cnt) < 20: # filter small noise
            continue
            
        # Larger epsilon for smoother, less craggy lines
        epsilon = 0.005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, closed=True)

        if len(approx) > 2:
            for i, point in enumerate(approx):
                x, y = point[0]
                if i == 0:
                    path_data.append(f"M {x} {y}")
                else:
                    path_data.append(f"L {x} {y}")
            path_data.append("Z")

    if path_data:
        path_str = " ".join(path_data)
        # Fill it! use evenodd to handle holes automatically
        svg_elements.append(
            f'  <path fill-rule="evenodd" d="{path_str}" fill="white" stroke="none"/>\n'
        )

    svg_elements.append('</svg>')

    with open(output_path, 'w') as f:
        f.writelines(svg_elements)

    print(f"Success! Solid velric logo saved to: {output_path}")

extract_solid_logo("clean_assets/velric_logo.jpeg", "clean_assets/velric_logo.svg")
