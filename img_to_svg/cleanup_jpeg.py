import cv2
import datetime
import numpy as np

def jpeg_to_lineart_svg(
    input_path, 
    output_path, 
    blur_kernel_size=5, 
    threshold_block_size=11, 
    threshold_c=4, 
    min_contour_area=5, 
    simplify_tolerance=1.0,
    stroke_width=1.5
):
    """
    Transforms a noisy JPEG into a clean line art SVG.
    
    Parameters:
    - input_path: Path to the input JPEG image.
    - output_path: Path to save the resulting SVG.
    - blur_kernel_size: (Odd integer) Amount of blur to reduce JPEG artifacts. Higher = less noise, but might soften fine lines.
    - threshold_block_size: (Odd integer) Size of the pixel neighborhood used to calculate the threshold.
    - threshold_c: Constant subtracted from the mean. Increase this to drop more background noise.
    - min_contour_area: Minimum area in pixels to keep a line. Increase to remove tiny stray dots/speckles.
    - simplify_tolerance: How strictly to follow the raw pixels. Higher = smoother, blockier lines and smaller file size.
    - stroke_width: The thickness of the lines in the final SVG.
    """
    
    # 1. Load the image in grayscale
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at '{input_path}'. Please check the path.")

    height, width = img.shape

    # 2. Denoise the image using Gaussian Blur
    # Make sure the kernel size is an odd number
    if blur_kernel_size % 2 == 0:
        blur_kernel_size += 1
        
    if blur_kernel_size > 0:
        blurred = cv2.GaussianBlur(img, (blur_kernel_size, blur_kernel_size), 0)
    else:
        blurred = img

    # 3. Binarize the image using Adaptive Thresholding
    # This is excellent for line art with uneven lighting or localized JPEG noise.
    # We invert it (THRESH_BINARY_INV) so lines become white (active) on a black background.
    if threshold_block_size % 2 == 0:
        threshold_block_size += 1
        
    binary = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 
        threshold_block_size,
        threshold_c
    )

    # 4. Extract the contours (the lines)
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # 5. Build the SVG content
    svg_elements = []
    # Set up the SVG canvas
    svg_elements.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">\n')
    svg_elements.append('  <rect width="100%" height="100%" fill="white"/>\n') # White background

    for cnt in contours:
        # Filter out tiny noise speckles
        if cv2.contourArea(cnt) < min_contour_area:
            continue

        # Simplify the contour to make the SVG paths smoother and smaller in file size
        approx = cv2.approxPolyDP(cnt, simplify_tolerance, closed=False)

        # Construct the SVG path data
        if len(approx) > 1:
            path_data = []
            for i, point in enumerate(approx):
                x, y = point[0]
                if i == 0:
                    path_data.append(f"M {x} {y}") # Move to the starting point
                else:
                    path_data.append(f"L {x} {y}") # Draw a line to the next point

            path_str = " ".join(path_data)
            svg_elements.append(
                f'  <path d="{path_str}" fill="none" stroke="black" '
                f'stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"/>\n'
            )

    svg_elements.append('</svg>')

    # 6. Write the elements to the SVG file
    with open(output_path, 'w') as f:
        f.writelines(svg_elements)

    print(f"Success! Clean line art saved to: {output_path}")


# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"clean_assets/velric_logo_{timestamp}.svg"

    # Tweak these parameters based on how noisy your input image is!
    jpeg_to_lineart_svg(
        input_path="velric_logo.jpeg",   # Replace with your image path
        output_path=output_filename,     # Now appends timestamp automatically
        blur_kernel_size=3,       # LOWERED: 3 or even 1. The image is clean. Lower blur preserves the sharp tips of the 'V'.
        threshold_block_size=21,  # INCREASED: A larger block size handles solid filled shapes (like thick text) much better.
        threshold_c=5,            # ADJUSTED: Keeps the extraction balanced for a dark background.
        min_contour_area=10,      # LOWERED: The image isn't heavily speckled, so we can lower this to keep the text details accurate.
        simplify_tolerance=0.5,   # SIGNIFICANTLY LOWERED: The logo has sharp, straight geometric lines. High tolerance will warp the font and 'V' corners.
        stroke_width=1.0
    )