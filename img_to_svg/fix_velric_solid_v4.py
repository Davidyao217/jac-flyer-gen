import cv2
import numpy as np

def extract_solid_logo(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    # Blur to smooth out the noise and cragginess initially
    blurred = cv2.GaussianBlur(img, (3, 3), 0)
        
    # Lower threshold to capture the missing faint chunk of the V
    _, binary = cv2.threshold(blurred, 12, 255, cv2.THRESH_BINARY)

    # Find contours including holes for letters like 'R'
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    height, width = img.shape
    svg_elements = []
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')

    path_data = []

    for cnt in contours:
        if cv2.contourArea(cnt) < 20: 
            continue
            
        # Larger epsilon forces the craggly polygons to collapse into their mathematical straight lines.
        # This gives a very crisp V, E, L, R, I, C.
        epsilon = 0.7
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
        svg_elements.append(
            f'  <path fill-rule="evenodd" d="{path_str}" fill="black" stroke="none" stroke-linejoin="round"/>\n'
        )

    svg_elements.append('</svg>')

    with open(output_path, 'w') as f:
        f.writelines(svg_elements)

    print(f"Success! Refined, smooth velric logo saved to: {output_path}")

extract_solid_logo("clean_assets/velric_logo.jpeg", "clean_assets/velric_logo.svg")
