import cv2
import numpy as np

img = cv2.imread("jaseci.png", cv2.IMREAD_GRAYSCALE)
# Background is 0, logo is >0. Normalize it to 0-255
norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)

# Threshold, so background is 0, logo is 255
_, binary = cv2.threshold(norm, 10, 255, cv2.THRESH_BINARY)

contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

height, width = binary.shape
svg_elements = []
svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')

path_data = []

# Filter noise and create a single SVG path for everything
# and use fill-rule="evenodd" so holes are transparent.
for cnt in contours:
    if cv2.contourArea(cnt) < 10:
        continue
    approx = cv2.approxPolyDP(cnt, 1.0, closed=True)
    if len(approx) > 2:
        for i, point in enumerate(approx):
            x, y = point[0]
            if i == 0:
                path_data.append(f"M {x} {y}")
            else:
                path_data.append(f"L {x} {y}")
        path_data.append("Z")

path_str = " ".join(path_data)
svg_elements.append(f'  <path fill-rule="evenodd" d="{path_str}" fill="black" stroke="none"/>\n')

svg_elements.append('</svg>')

with open("clean_assets/jaseci_logo.svg", "w") as f:
    f.writelines(svg_elements)

print("Saved SVG using evenodd")
