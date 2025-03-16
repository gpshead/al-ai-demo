#!/usr/bin/env python3
"""
Test script to generate PNG files using Pillow for comparison.
"""
import sys
from PIL import Image
import numpy as np
from eps_to_png import parse_eps_file, SimplePostScriptInterpreter

def convert_eps_to_png_pillow(eps_file, png_file):
    """
    Convert an EPS file to a PNG file using Pillow for the PNG encoding.
    
    Args:
        eps_file: Path to the EPS file
        png_file: Path to the output PNG file
    """
    # Parse EPS file
    bbox, commands = parse_eps_file(eps_file)
    
    # Calculate dimensions from bounding box
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    
    # Create interpreter and execute commands
    interpreter = SimplePostScriptInterpreter(width, height, bbox)
    bitmap = interpreter.execute(commands)
    
    # Convert bitmap to numpy array
    array = np.array(bitmap.pixels, dtype=np.uint8)
    
    # Create PIL Image from array
    img = Image.fromarray(array, mode='L')
    
    # Save as PNG
    img.save(png_file)
    
    print(f"Converted {eps_file} to {png_file} using Pillow")
    print(f"Dimensions: {width}x{height} pixels")
    print(f"Bounding box: {bbox}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_pillow_png.py input.eps output.png")
        sys.exit(1)
    
    convert_eps_to_png_pillow(sys.argv[1], sys.argv[2])