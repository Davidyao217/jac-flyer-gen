import cv2
import numpy as np

def convert_michigan_to_svg(input_path, output_path):
    """
    Convert the Michigan block M logo (yellow on white) to SVG.
    The M is a solid yellow geometric shape, so we isolate it via HSV color
    thresholding on the yellow hue, then trace filled contours.
    """
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image at '{input_path}'")

    height, width = img.shape[:2]

    # Convert to HSV to isolate the maize/yellow color
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Yellow/maize hue range in HSV (OpenCV uses H: 0-180)
    lower_yellow = np.array([15, 100, 100])
    upper_yellow = np.array([35, 255, 255])
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Clean up the mask
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Find contours with hierarchy for holes (like inner white areas of the M)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    svg_elements = []
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')

    path_data = []

    for cnt in contours:
        if cv2.contourArea(cnt) < 50:
            continue

        # Use a tight epsilon for the geometric block M shape
        epsilon = 0.5
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

    print(f"Success! Michigan block M saved to: {output_path}")

convert_michigan_to_svg("img_to_svg/michigan_block.png", "clean_assets/michigan_block.svg")
