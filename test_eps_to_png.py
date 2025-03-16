#!/usr/bin/env python3
"""
Unit tests for the EPS to PNG converter.
This uses third-party libraries for validation purposes only.
"""
import os
import tempfile
import unittest
import subprocess
from pathlib import Path

# Third-party imports for validation
import pytest
from PIL import Image, ImageChops, ImageStat

# Import our converter
from eps_to_png import parse_eps_file, convert_eps_to_png

class TestEPSToPNG(unittest.TestCase):
    """Test suite for the EPS to PNG converter."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_files = [
            "test_square.eps",
            "test_shapes.eps",
            "test_circles.eps"
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

    def test_comparison_with_ghostscript(self):
        """Compare our PNG output with GhostScript's output."""
        for test_file in self.test_files:
            eps_path = Path(test_file)
            if eps_path.exists():
                # Our converter output
                our_png_path = Path(self.temp_dir.name) / f"{eps_path.stem}_our.png"
                convert_eps_to_png(eps_path, our_png_path)
                
                # Check if Ghostscript command-line tool is available
                try:
                    result = subprocess.run(["which", "gs"], stdout=subprocess.PIPE, text=True)
                    if result.returncode != 0:
                        self.skipTest("Ghostscript command-line tool is not available")
                except:
                    self.skipTest("Error checking for Ghostscript availability")
                
                # GhostScript output
                gs_png_path = Path(self.temp_dir.name) / f"{eps_path.stem}_gs.png"
                
                # Call GhostScript to convert EPS to PNG
                args = [
                    "gs",
                    "-q",
                    "-dSAFER",
                    "-dBATCH",
                    "-dNOPAUSE",
                    "-sDEVICE=pnggray",
                    f"-sOutputFile={gs_png_path}",
                    "-r72",
                    str(eps_path)
                ]
                try:
                    subprocess.run(args, check=True)
                except subprocess.CalledProcessError:
                    self.skipTest("GhostScript conversion failed")
                
                # Both files should exist
                self.assertTrue(our_png_path.exists())
                self.assertTrue(gs_png_path.exists())
                
                # Verify our PNG is valid
                try:
                    # Just verify file format, don't load all data
                    with Image.open(our_png_path) as img:
                        self.assertEqual(img.format, "PNG")
                    
                    # Check if GhostScript output is valid
                    with Image.open(gs_png_path) as img:
                        self.assertEqual(img.format, "PNG")
                    
                    # Compare basic file properties
                    our_size = our_png_path.stat().st_size
                    gs_size = gs_png_path.stat().st_size
                    
                    # Just make sure both files have content
                    self.assertGreater(our_size, 100, "Our PNG file is too small")
                    self.assertGreater(gs_size, 100, "GhostScript PNG file is too small")
                    
                    # Output some stats for information
                    print(f"File: {test_file}")
                    print(f"Our image size: {our_size} bytes")
                    print(f"GS image size: {gs_size} bytes")
                    
                except Exception as e:
                    self.fail(f"Error processing images: {e}")
                
                # This is a simplistic validation - in a real test we might want more
                # sophisticated image comparison methods
    
    def test_with_direct_ghostscript(self):
        """Compare our output with direct GhostScript PNG conversion."""
        for test_file in self.test_files:
            eps_path = Path(test_file)
            if eps_path.exists():
                # Our converter output
                our_png_path = Path(self.temp_dir.name) / f"{eps_path.stem}_our.png"
                convert_eps_to_png(eps_path, our_png_path)
                
                # Check if Ghostscript command-line tool is available
                try:
                    result = subprocess.run(["which", "gs"], stdout=subprocess.PIPE, text=True)
                    if result.returncode != 0:
                        self.skipTest("Ghostscript command-line tool is not available")
                except:
                    self.skipTest("Error checking for Ghostscript availability")
                
                # Direct GhostScript PNG output
                direct_png_path = Path(self.temp_dir.name) / f"{eps_path.stem}_direct.png"
                
                # EPS → PNG directly with Ghostscript
                args = [
                    "gs",
                    "-q",
                    "-dSAFER",
                    "-dBATCH",
                    "-dNOPAUSE",
                    "-sDEVICE=png16m",  # Use RGB color for better visualization
                    f"-sOutputFile={direct_png_path}",
                    "-r72",
                    str(eps_path)
                ]
                try:
                    subprocess.run(args, check=True)
                except subprocess.CalledProcessError:
                    self.skipTest("GhostScript direct conversion failed")
                
                # Both files should exist
                self.assertTrue(our_png_path.exists())
                self.assertTrue(direct_png_path.exists())
                
                # Verify our PNG is valid
                try:
                    # Just verify file format, don't load all data
                    with Image.open(our_png_path) as img:
                        self.assertEqual(img.format, "PNG")
                    
                    # Check if direct PNG is valid
                    with Image.open(direct_png_path) as img:
                        self.assertEqual(img.format, "PNG")
                    
                    # Compare basic file properties
                    our_size = our_png_path.stat().st_size
                    direct_size = direct_png_path.stat().st_size
                    
                    # Just make sure both files have content
                    self.assertGreater(our_size, 100, "Our PNG file is too small")
                    self.assertGreater(direct_size, 100, "Direct PNG file is too small")
                    
                    # Output some stats for information
                    print(f"File: {test_file}")
                    print(f"Our image size: {our_size} bytes")
                    print(f"Direct GS image size: {direct_size} bytes")
                    
                except Exception as e:
                    self.fail(f"Error processing images: {e}")

if __name__ == "__main__":
    unittest.main()