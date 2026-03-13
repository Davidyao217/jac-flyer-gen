import cv2
import numpy as np

def extract_solid_logo(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    # 1. Blur to remove craggy JPEG noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
        
    # 2. Use a fixed global threshold because the large 'V' is dim
    #    (Intensity ~ 40, whereas text is ~ 100).
    #    Otsu calculated ~93, cutting off the V entirely.
    _, binary = cv2.threshold(blurred, 25, 255, cv2.THRESH_BINARY)

    # 3. Find contours including holes for letters like 'R'
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    height, width = img.shape
    svg_elements = []
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')

    # We want a single path with all contours, using evenodd for holes
    path_data = []

    for cnt in contours:
        if cv2.contourArea(cnt) < 15: # Safety noise filter
            continue
            
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
        # evenodd automatically makes the 'R' hole transparent
        svg_elements.append(
            f'  <path fill-rule="evenodd" d="{path_str}" fill="white" stroke="none"/>\n'
        )

    svg_elements.append('</svg>')

    with open(output_path, 'w') as f:
        f.writelines(svg_elements)

    print(f"Success! Solid velric logo (including large V) saved to: {output_path}")

extract_solid_logo("clean_assets/velric_logo.jpeg", "clean_assets/velric_logo.svg")
