import vtracer
from PIL import Image
import os

def convert_png_to_svg_smooth(input_file, output_file, scale_factor=1.5):
    temp_file = "temp_upscaled.png"
    
    # 1. Upscale the image to provide better data for the tracer
    with Image.open(input_file) as img:
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        # Lanczos resampling helps smooth edges during the upscale
        upscaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        upscaled_img.save(temp_file)

    # 2. Run VTracer on the temporary upscaled image
    vtracer.convert_image_to_svg_py(
        temp_file,
        output_file,
        colormode='color',
        mode='spline',
        filter_speckle=0,        
        path_precision=1000,         
        corner_threshold=100000
    )

    # 3. Clean up the temporary file
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    print(f"Successfully converted {input_file} to {output_file} with {scale_factor}x upscaling.")

convert_png_to_svg_smooth("clean_assets/ship_logo-removebg-preview.png", "clean_assets/ship_logo_2color.svg")