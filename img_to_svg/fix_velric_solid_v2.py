import cv2
import numpy as np

def extract_solid_logo(input_path, output_path):
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

    # Blur to remove craggy JPEG noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
        
    # Adaptive threshold finds edges of the V even if it has a gradient.
    # It might hollow out the center.
    binary = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 5
    )

    # Use RETR_EXTERNAL to get only the outermost contour of each shape.
    # This automatically "fills in" any hollow centers caused by adaptiveThreshold.
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    height, width = img.shape
    svg_elements = []
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')

    # We only want the path data
    path_data = []

    for cnt in contours:
        # Tweak the area slightly so we don't pick up too much speckle noise
        if cv2.contourArea(cnt) < 20: 
            continue
            
        # Keep epsilon small enough for sharp edges but large enough to smooth crags
        epsilon = 0.005 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, closed=True)

        if len(approx) > 2:
            for i, point in enumerate(approx):
                x, y = point[0]
                if i == 0:
                    path_data.append(f"M {x} {y}")
                else:
                    path_data.append(f"L {x} {y}")
            # Ensure the path is closed for a solid fill
            path_data.append("Z")

    if path_data:
        path_str = " ".join(path_data)
        # Force a solid fill using fill-rule="nonzero" (default) or just rely on RETR_EXTERNAL
        svg_elements.append(
            f'  <path d="{path_str}" fill="white" stroke="none"/>\n'
        )

    svg_elements.append('</svg>')

    with open(output_path, 'w') as f:
        f.writelines(svg_elements)

    print(f"Success! Solid velric logo saved to: {output_path}")

extract_solid_logo("clean_assets/velric_logo.jpeg", "clean_assets/velric_logo.svg")
