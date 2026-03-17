import cv2
import numpy as np

def convert_nvidia_to_svg(input_path, output_path):
    """
    Convert the NVIDIA logo (green eye icon + black text) from PNG to SVG.
    This logo has two distinct color regions:
    - Green (#76B900) eye/icon
    - Black text "nVIDIA"
    We trace both and combine them into a single SVG with fill="black".
    """
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at '{input_path}'")

    height, width = img.shape[:2]

    # Convert to HSV for green detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # --- Extract green regions (the eye icon) ---
    lower_green = np.array([25, 50, 50])
    upper_green = np.array([85, 255, 255])
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # --- Extract black/dark regions (the text) ---
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, black_mask = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)

    # Combine both masks
    combined_mask = cv2.bitwise_or(green_mask, black_mask)

    # Clean up
    kernel = np.ones((3, 3), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours with hierarchy for proper holes
    contours, hierarchy = cv2.findContours(combined_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    svg_elements = []
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')

    path_data = []

    for cnt in contours:
        if cv2.contourArea(cnt) < 30:
            continue

        # Use tight tolerance for the eye curves and text
        epsilon = 1.0
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
            f'  <path fill-rule="evenodd" d="{path_str}" fill="black" stroke="none"/>\n'
        )

    svg_elements.append('</svg>')

    with open(output_path, 'w') as f:
        f.writelines(svg_elements)

    print(f"Success! NVIDIA logo saved to: {output_path}")

convert_nvidia_to_svg("img_to_svg/nvidia-logo-vert.png", "clean_assets/nvidia_logo.svg")
