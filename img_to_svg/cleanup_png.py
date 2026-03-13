import cv2

def convert_to_clean_svg(input_path, output_path, min_line_length=45, smooth_factor=0.002):
    print(f"Loading '{input_path}'...")
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        print(f"Error: Could not find '{input_path}'.")
        return

    # Get image dimensions for the SVG canvas
    height, width = img.shape
    
    # Convert to binary (white lines on black background)
    _, binary = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)

    # Find the lines
    print("Tracing lines...")
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Prepare the SVG file structure
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">',
        '  <style>',
        '    path { fill: none; stroke: #000000; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }',
        '  </style>'
    ]

    kept_lines = 0
    # Process each line
    for contour in contours:
        length = cv2.arcLength(contour, closed=False)
        
        # 1. Filter out the noise (leaves, bricks, short squiggles)
        if length > min_line_length:
            
            # 2. Smooth and straighten the architectural lines
            epsilon = smooth_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, False)
            
            # 3. Convert the OpenCV coordinates into an SVG path
            if len(approx) > 1:
                # Start the path with 'M' (Move to), then join the rest with 'L' (Line to)
                path_data = "M " + " L ".join([f"{pt[0][0]},{pt[0][1]}" for pt in approx])
                svg_lines.append(f'  <path d="{path_data}" />')
                kept_lines += 1

    svg_lines.append('</svg>')

    # Write the results directly to an SVG file
    with open(output_path, "w") as f:
        f.write("\n".join(svg_lines))

    print(f"Success! Kept {kept_lines} clean architectural lines.")
    print(f"Saved directly as '{output_path}'.")

# --- Run the script ---
# Make sure your original 'wee.png' is in the same folder!
convert_to_clean_svg('tower.png', 'cleaned_building.svg', min_line_length=45, smooth_factor=0.002)