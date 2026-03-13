import cv2
import numpy as np

def extract_logo(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    blurred = cv2.GaussianBlur(img, (3, 3), 0)
        
    binary = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 
        21,
        5
    )

    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    height, width = img.shape
    svg_elements = []
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')
    # No background dict. Just transparent!
    
    for cnt in contours:
        if cv2.contourArea(cnt) < 10:
            continue
            
        approx = cv2.approxPolyDP(cnt, 0.5, closed=False)

        if len(approx) > 1:
            path_data = []
            for i, point in enumerate(approx):
                x, y = point[0]
                if i == 0:
                    path_data.append(f"M {x} {y}")
                else:
                    path_data.append(f"L {x} {y}")

            path_str = " ".join(path_data)
            svg_elements.append(
                f'  <path d="{path_str}" fill="none" stroke="black" '
                f'stroke-width="1.0" stroke-linecap="round" stroke-linejoin="round"/>\n'
            )

    svg_elements.append('</svg>')

    with open(output_path, 'w') as f:
        f.writelines(svg_elements)

    print(f"Success! velric logo saved to: {output_path}")

extract_logo("clean_assets/velric_logo.jpeg", "clean_assets/velric_logo.svg")
