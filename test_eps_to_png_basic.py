#!/usr/bin/env python3
"""
Basic unit tests for the EPS to PNG converter.
This only requires PIL (Pillow) for validation.
"""
import os
import tempfile
import unittest
from pathlib import Path

# Third-party imports for validation
from PIL import Image

# Import our converter
from eps_to_png import parse_eps_file, convert_eps_to_png

class TestEPSToPNGBasic(unittest.TestCase):
    """Basic test suite for the EPS to PNG converter."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_files = [
            "test_square.eps",
            "test_shapes.eps",
            "test_circles.eps",
            "test_commands.eps"
        ]
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()
    
    def test_parse_eps_file(self):
        """Test EPS file parsing."""
        for test_file in self.test_files:
            test_path = Path(test_file)
            if test_path.exists():
                bbox, commands = parse_eps_file(test_path)
                
                # Check that bounding box is valid
                self.assertEqual(len(bbox), 4)
                self.assertGreaterEqual(bbox[2], bbox[0])  # urx >= llx
                self.assertGreaterEqual(bbox[3], bbox[1])  # ury >= lly
                
                # Check that we extracted commands
                self.assertGreater(len(commands), 0)
                
                # Check for common PostScript commands
                all_commands = ' '.join(commands)
                self.assertIn('newpath', all_commands)
                
                # Check for at least one drawing command
                drawing_commands = ['moveto', 'lineto', 'arc', 'stroke', 'fill']
                self.assertTrue(any(cmd in all_commands for cmd in drawing_commands), 
                              f"No drawing commands found in {test_file}")
    
    def test_eps_conversion_dimensions(self):
        """Test that the generated PNGs have correct dimensions."""
        for test_file in self.test_files:
            eps_path = Path(test_file)
            if eps_path.exists():
                # Get bounding box from the EPS file
                bbox, _ = parse_eps_file(eps_path)
                expected_width = bbox[2] - bbox[0]
                expected_height = bbox[3] - bbox[1]
                
                # Convert EPS to PNG
                png_path = Path(self.temp_dir.name) / f"{eps_path.stem}.png"
                convert_eps_to_png(eps_path, png_path)
                
                # Check that the PNG file exists
                self.assertTrue(png_path.exists())
                
                # Check dimensions using PIL
                with Image.open(png_path) as img:
                    self.assertEqual(img.width, expected_width)
                    self.assertEqual(img.height, expected_height)
    
    def test_png_format_validity(self):
        """Test that the generated PNG files are valid."""
        for test_file in self.test_files:
            eps_path = Path(test_file)
            if eps_path.exists():
                # Convert EPS to PNG
                png_path = Path(self.temp_dir.name) / f"{eps_path.stem}.png"
                convert_eps_to_png(eps_path, png_path)
                
                # Validate PNG using PIL
                try:
                    with Image.open(png_path) as img:
                        # This will raise an exception if the PNG is invalid
                        img.verify()
                    # Load the image to check basic properties
                    with Image.open(png_path) as img:
                        self.assertEqual(img.format, "PNG")
                        # Check that it's a grayscale image
                        self.assertIn(img.mode, ("L", "1"))
                except Exception as e:
                    self.fail(f"Invalid PNG generated for {test_file}: {e}")
    
    def test_image_has_content(self):
        """Test that the generated PNG has actual content."""
        for test_file in self.test_files:
            eps_path = Path(test_file)
            if eps_path.exists():
                # Convert EPS to PNG
                png_path = Path(self.temp_dir.name) / f"{eps_path.stem}.png"
                convert_eps_to_png(eps_path, png_path)
                
                # Check that the file exists and has a non-zero size
                self.assertTrue(png_path.exists())
                self.assertGreater(png_path.stat().st_size, 100)  # Should be larger than 100 bytes
                
                # Verify the file is a valid PNG using PIL
                try:
                    img = Image.open(png_path)
                    # Check the file format and dimensions
                    self.assertEqual(img.format, "PNG")
                    
                    # Get bounding box from the EPS file
                    bbox, _ = parse_eps_file(eps_path)
                    expected_width = bbox[2] - bbox[0]
                    expected_height = bbox[3] - bbox[1]
                    
                    self.assertEqual(img.width, expected_width)
                    self.assertEqual(img.height, expected_height)
                    
                    # Load pixel data
                    img_data = list(img.getdata())
                    total_pixels = len(img_data)
                    
                    # Count non-white pixels
                    non_white = sum(1 for p in img_data if p < 255)
                    
                    # There should be a significant number of non-white pixels in each image
                    self.assertGreater(non_white, 0, "Image appears to be completely white")
                    
                    # Print some stats
                    print(f"File: {test_file}")
                    print(f"Dimensions: {img.width}x{img.height}")
                    print(f"File size: {png_path.stat().st_size} bytes")
                    print(f"Non-white pixels: {non_white}/{total_pixels} ({non_white/total_pixels:.1%})")
                    
                    img.close()
                except Exception as e:
                    self.fail(f"Invalid PNG generated for {test_file}: {e}")
                    
    def test_output_file_properties(self):
        """Test properties of the output PNG files."""
        # With compression enabled, files will be much smaller
        
        for test_file in self.test_files:
            eps_path = Path(test_file)
            if eps_path.exists():
                # Convert EPS to PNG
                png_path = Path(self.temp_dir.name) / f"{eps_path.stem}.png"
                convert_eps_to_png(eps_path, png_path)
                
                # Check that the file exists
                self.assertTrue(png_path.exists(), f"PNG file was not created for {test_file}")
                
                # Check file size
                file_size = png_path.stat().st_size
                
                # Compressed PNG files should at least be 100 bytes
                self.assertGreater(file_size, 100, 
                                 f"PNG file for {test_file} is suspiciously small ({file_size} bytes)")
                
                # Create uncompressed version for comparison
                uncompressed_png_path = Path(self.temp_dir.name) / f"{eps_path.stem}_uncompressed.png"
                convert_eps_to_png(eps_path, uncompressed_png_path, compress=False)
                
                # Verify uncompressed exists
                self.assertTrue(uncompressed_png_path.exists())
                
                # Get uncompressed size
                uncompressed_size = uncompressed_png_path.stat().st_size
                
                # Compressed should be smaller than uncompressed
                self.assertLess(file_size, uncompressed_size,
                              f"Compressed PNG ({file_size} bytes) should be smaller than uncompressed ({uncompressed_size} bytes)")
                
                # Check PNG header (first 8 bytes)
                with open(png_path, 'rb') as f:
                    png_signature = f.read(8)
                    expected_signature = bytes([137, 80, 78, 71, 13, 10, 26, 10])
                    self.assertEqual(png_signature, expected_signature, 
                                   f"PNG file for {test_file} has invalid signature")
                    
                # Optionally check for IHDR chunk
                with open(png_path, 'rb') as f:
                    f.read(8)  # Skip signature
                    chunk_length = int.from_bytes(f.read(4), byteorder='big')
                    chunk_type = f.read(4)
                    self.assertEqual(chunk_type, b'IHDR', 
                                   f"PNG file for {test_file} has invalid chunk structure")
                    
                # Print information
                print(f"\nPNG file properties for {test_file}:")
                print(f"  File size: {file_size} bytes")
                print(f"  File path: {png_path}")
                
                # Try to get basic image info without loading pixel data
                try:
                    with Image.open(png_path) as img:
                        print(f"  Image format: {img.format}")
                        print(f"  Image mode: {img.mode}")
                        print(f"  Image size: {img.width}x{img.height}")
                        
                        # Verify dimensions match bounding box
                        bbox, _ = parse_eps_file(eps_path)
                        expected_width = bbox[2] - bbox[0]
                        expected_height = bbox[3] - bbox[1]
                        self.assertEqual(img.width, expected_width)
                        self.assertEqual(img.height, expected_height)
                except Exception as e:
                    print(f"  Warning: Could not get image info: {e}")
            else:
                print(f"Skipping file {test_file} - not found")

if __name__ == "__main__":
    unittest.main()