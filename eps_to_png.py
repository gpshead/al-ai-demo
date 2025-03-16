#!/usr/bin/env python3
"""
A simple EPS to PNG converter that doesn't rely on third-party libraries.
Supports a limited subset of PostScript commands and creates uncompressed PNG files.
"""

class Bitmap:
    """
    Simple bitmap class for storing image data.
    """
    def __init__(self, width, height):
        """
        Initialize a bitmap with the given dimensions.
        
        Args:
            width: Width of the bitmap
            height: Height of the bitmap
        """
        self.width = width
        self.height = height
        # Initialize with white pixels (255)
        self.pixels = [[255 for _ in range(width)] for _ in range(height)]
    
    def set_pixel(self, x, y, value):
        """
        Set a pixel value at the given coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            value: Pixel value (0-255)
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = value
    
    def draw_line(self, x1, y1, x2, y2, color=0):
        """
        Draw a line from (x1, y1) to (x2, y2) using Bresenham's algorithm.
        
        Args:
            x1, y1: Starting point
            x2, y2: Ending point
            color: Line color (default: 0 = black)
        """
        # Implementation of Bresenham's line algorithm
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            self.set_pixel(x1, y1, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
    
    def draw_circle(self, xc, yc, radius, color=0):
        """
        Draw a circle using the Midpoint Circle Algorithm.
        
        Args:
            xc, yc: Center coordinates
            radius: Circle radius
            color: Circle color (default: 0 = black)
        """
        x = 0
        y = radius
        d = 1 - radius
        
        self._draw_circle_points(xc, yc, x, y, color)
        
        while y > x:
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1
            self._draw_circle_points(xc, yc, x, y, color)
    
    def _draw_circle_points(self, xc, yc, x, y, color):
        """
        Helper method to draw the 8 points of a circle at once.
        """
        self.set_pixel(xc + x, yc + y, color)
        self.set_pixel(xc - x, yc + y, color)
        self.set_pixel(xc + x, yc - y, color)
        self.set_pixel(xc - x, yc - y, color)
        self.set_pixel(xc + y, yc + x, color)
        self.set_pixel(xc - y, yc + x, color)
        self.set_pixel(xc + y, yc - x, color)
        self.set_pixel(xc - y, yc - x, color)
    
    def draw_arc(self, xc, yc, radius, start_angle, end_angle, color=0):
        """
        Draw an arc using a simple approach.
        
        Args:
            xc, yc: Center coordinates
            radius: Arc radius
            start_angle, end_angle: Start and end angles in degrees
            color: Arc color (default: 0 = black)
        """
        import math
        
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Ensure end_angle > start_angle
        if end_rad < start_rad:
            end_rad += 2 * math.pi
        
        # Number of segments depends on radius for smoothness
        segments = max(20, int(radius * 0.5))
        
        # Draw the arc using line segments
        prev_x, prev_y = None, None
        for i in range(segments + 1):
            # Calculate angle for this segment
            angle = start_rad + (end_rad - start_rad) * i / segments
            
            # Calculate point on the arc
            x = int(xc + radius * math.cos(angle))
            y = int(yc + radius * math.sin(angle))
            
            if prev_x is not None:
                self.draw_line(prev_x, prev_y, x, y, color)
            
            prev_x, prev_y = x, y
    
    def fill_polygon(self, points, color=0):
        """
        Simple scanline polygon fill algorithm.
        
        Args:
            points: List of (x, y) tuples defining the polygon
            color: Fill color (default: 0 = black)
        """
        # Convert points to integer coordinates
        int_points = [(int(x), int(y)) for x, y in points]
        
        # Find min and max y
        y_min = min(y for _, y in int_points)
        y_max = max(y for _, y in int_points)
        
        # For each scanline
        for y in range(y_min, y_max + 1):
            # Find intersections
            intersections = []
            
            for i in range(len(int_points)):
                x1, y1 = int_points[i]
                x2, y2 = int_points[(i + 1) % len(int_points)]
                
                # Skip horizontal edges
                if y1 == y2:
                    continue
                
                # Check if scanline intersects this edge
                if y1 <= y <= y2 or y2 <= y <= y1:
                    # Calculate x coordinate of intersection
                    if y2 - y1 != 0:  # Avoid division by zero
                        x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                        intersections.append(int(x))
            
            # Sort intersections
            intersections.sort()
            
            # Fill between intersection pairs
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    for x in range(intersections[i], intersections[i + 1] + 1):
                        self.set_pixel(x, y, color)


class SimplePostScriptInterpreter:
    """
    A very simplified PostScript interpreter that can handle basic drawing commands.
    """
    def __init__(self, width, height, bbox):
        """
        Initialize the interpreter.
        
        Args:
            width: Width of the output bitmap
            height: Height of the output bitmap
            bbox: Bounding box [llx, lly, urx, ury]
        """
        self.bitmap = Bitmap(width, height)
        self.stack = []
        self.current_path = []
        self.current_point = None
        self.line_width = 1
        self.gray_level = 0  # 0 = black, 255 = white
        
        # Transformation parameters
        self.x_offset = -bbox[0]
        self.y_offset = -bbox[1]
        
        # Store the bounding box for coordinate transformation
        self.bbox = bbox
    
    def transform_coords(self, x, y):
        """
        Transform PostScript coordinates to bitmap coordinates.
        
        Args:
            x, y: PostScript coordinates
            
        Returns:
            tuple: Bitmap coordinates (x, y)
        """
        # Apply offsets
        x = x + self.x_offset
        y = y + self.y_offset
        
        # Flip Y coordinate (PostScript has origin at bottom-left, bitmap at top-left)
        y = self.bitmap.height - y
        
        return x, y
    
    def execute(self, commands):
        """
        Execute a list of PostScript commands.
        
        Args:
            commands: List of PostScript commands
        """
        for cmd in commands:
            self._process_command(cmd)
        
        return self.bitmap
    
    def _process_command(self, cmd):
        """
        Process a single PostScript command.
        
        Args:
            cmd: A PostScript command string
        """
        tokens = cmd.split()
        i = 0
        
        while i < len(tokens):
            token = tokens[i]
            
            # Handle numbers
            if token.replace('.', '', 1).replace('-', '', 1).isdigit():
                self.stack.append(float(token))
            
            # Handle commands
            elif token == "moveto":
                y = self.stack.pop()
                x = self.stack.pop()
                self.current_point = (x, y)
                if not self.current_path:
                    self.current_path = [(x, y)]
                else:
                    self.current_path.append((x, y))
            
            elif token == "lineto":
                y = self.stack.pop()
                x = self.stack.pop()
                if self.current_point:
                    self.current_path.append((x, y))
                    self.current_point = (x, y)
            
            elif token == "rlineto":
                dy = self.stack.pop()
                dx = self.stack.pop()
                if self.current_point:
                    x, y = self.current_point
                    new_x, new_y = x + dx, y + dy
                    self.current_path.append((new_x, new_y))
                    self.current_point = (new_x, new_y)
            
            elif token == "rmoveto":
                dy = self.stack.pop()
                dx = self.stack.pop()
                if self.current_point:
                    x, y = self.current_point
                    self.current_point = (x + dx, y + dy)
                    self.current_path.append(self.current_point)
            
            elif token == "closepath":
                if self.current_path and len(self.current_path) > 1:
                    self.current_path.append(self.current_path[0])
                    self.current_point = self.current_path[0]
            
            elif token == "arc":
                # arc takes 5 arguments: x y r angle1 angle2
                angle2 = self.stack.pop()
                angle1 = self.stack.pop()
                radius = self.stack.pop()
                y = self.stack.pop()
                x = self.stack.pop()
                self._draw_arc(x, y, radius, angle1, angle2)
            
            elif token == "stroke":
                self._stroke_path()
            
            elif token == "fill":
                self._fill_path()
            
            elif token == "newpath":
                self.current_path = []
                self.current_point = None
            
            elif token == "setlinewidth":
                self.line_width = int(max(1, self.stack.pop()))
            
            elif token == "setgray":
                gray = self.stack.pop()
                # Convert from PostScript gray (0=black, 1=white) to our bitmap (0=black, 255=white)
                self.gray_level = int(gray * 255)
                
            # We'll ignore these commands in our simplified interpreter
            elif token in ["gsave", "grestore", "showpage"]:
                pass
            
            i += 1
    
    def _draw_arc(self, x, y, radius, start_angle, end_angle):
        """
        Add an arc to the current path.
        
        Args:
            x, y: Center coordinates
            radius: Arc radius
            start_angle, end_angle: Start and end angles in degrees
        """
        import math
        
        # Number of segments depends on radius for smoothness
        segments = max(20, int(radius * 0.5))
        
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Ensure end_angle > start_angle
        if end_rad < start_rad and end_angle - start_angle <= 0:
            end_rad += 2 * math.pi
        
        # Calculate points on the arc
        for i in range(segments + 1):
            # Calculate angle for this segment
            angle = start_rad + (end_rad - start_rad) * i / segments
            
            # Calculate point on the arc
            point_x = x + radius * math.cos(angle)
            point_y = y + radius * math.sin(angle)
            
            # Add point to the path
            if i == 0 and not self.current_path:
                self.current_path.append((point_x, point_y))
                self.current_point = (point_x, point_y)
            else:
                self.current_path.append((point_x, point_y))
                self.current_point = (point_x, point_y)
    
    def _stroke_path(self):
        """
        Stroke the current path.
        """
        if len(self.current_path) < 2:
            return
            
        for i in range(len(self.current_path) - 1):
            x1, y1 = self.current_path[i]
            x2, y2 = self.current_path[i + 1]
            
            # Transform coordinates to bitmap space
            x1, y1 = self.transform_coords(x1, y1)
            x2, y2 = self.transform_coords(x2, y2)
            
            # Convert to integers
            x1, y1 = int(x1), int(y1)
            x2, y2 = int(x2), int(y2)
            
            self.bitmap.draw_line(x1, y1, x2, y2, self.gray_level)
        
        self.current_path = []
    
    def _fill_path(self):
        """
        Fill the current path.
        """
        if len(self.current_path) < 3:
            return
            
        # Transform all points to bitmap coordinates
        transformed_path = [self.transform_coords(x, y) for x, y in self.current_path]
        self.bitmap.fill_polygon(transformed_path, self.gray_level)
        self.current_path = []


def parse_eps_file(eps_file_path):
    """
    Parse an EPS file and extract the bounding box and PostScript commands.
    
    Args:
        eps_file_path: Path to the EPS file
        
    Returns:
        tuple: (bounding_box, commands)
    """
    with open(eps_file_path, 'r') as f:
        content = f.readlines()
    
    # Extract bounding box
    bounding_box = None
    commands = []
    
    for line in content:
        if line.strip().startswith('%%BoundingBox:'):
            # Extract bounding box values
            bbox_parts = line.split(':', 1)[1].strip().split()
            bounding_box = [int(x) for x in bbox_parts]
        elif not line.strip().startswith('%'):
            # Collect non-comment lines as PostScript commands
            commands.append(line.strip())
    
    if bounding_box is None:
        raise ValueError("No bounding box found in EPS file")
        
    return bounding_box, commands


def encode_png(bitmap, output_file, compress=True):
    """
    Encode a bitmap as a PNG file with optional compression.
    
    Args:
        bitmap: The bitmap to encode
        output_file: The output file path
        compress: Whether to use compression (defaults to True)
    """
    import zlib  # Standard library module
    
    with open(output_file, 'wb') as f:
        # PNG signature
        f.write(bytes([137, 80, 78, 71, 13, 10, 26, 10]))
        
        # IHDR chunk
        ihdr_data = bytearray()
        # Width (4 bytes)
        ihdr_data.extend(bitmap.width.to_bytes(4, byteorder='big'))
        # Height (4 bytes)
        ihdr_data.extend(bitmap.height.to_bytes(4, byteorder='big'))
        # Bit depth (1 byte)
        ihdr_data.append(8)
        # Color type (1 byte) - 0 for grayscale
        ihdr_data.append(0)
        # Compression method (1 byte) - 0 for DEFLATE
        ihdr_data.append(0)
        # Filter method (1 byte) - 0 for basic filtering
        ihdr_data.append(0)
        # Interlace method (1 byte) - 0 for no interlacing
        ihdr_data.append(0)
        
        # Write IHDR chunk
        write_png_chunk(f, b'IHDR', ihdr_data)
        
        # IDAT chunk (image data)
        # For each scanline: filter type byte (0) + row data
        filtered_data = bytearray()
        for row in bitmap.pixels:
            # Filter type byte (0 = no filtering)
            filtered_data.append(0)
            # Row data
            filtered_data.extend(row)
        
        # Compress the filtered data using zlib
        if compress:
            # Level 9 is maximum compression
            idat_data = zlib.compress(filtered_data, level=9)
        else:
            # Use minimal compression (fastest)
            idat_data = zlib.compress(filtered_data, level=0)
        
        # Write IDAT chunk
        write_png_chunk(f, b'IDAT', idat_data)
        
        # IEND chunk (empty)
        write_png_chunk(f, b'IEND', bytearray())


def write_png_chunk(file, chunk_type, data):
    """
    Write a PNG chunk to a file.
    
    Args:
        file: The file to write to
        chunk_type: The chunk type (4 bytes)
        data: The chunk data
    """
    # Length (4 bytes)
    file.write(len(data).to_bytes(4, byteorder='big'))
    
    # Chunk type (4 bytes)
    file.write(chunk_type)
    
    # Chunk data
    file.write(data)
    
    # CRC (4 bytes)
    crc = calculate_crc(chunk_type + data)
    file.write(crc.to_bytes(4, byteorder='big'))


def calculate_crc(data):
    """
    Calculate the CRC32 of data.
    
    Args:
        data: The data to calculate the CRC for
        
    Returns:
        The CRC32 value
    """
    # Simple CRC32 implementation
    crc = 0xFFFFFFFF
    
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xEDB88320
            else:
                crc = crc >> 1
    
    return ~crc & 0xFFFFFFFF


def convert_eps_to_png(eps_file, png_file, compress=True):
    """
    Convert an EPS file to a PNG file.
    
    Args:
        eps_file: Path to the EPS file
        png_file: Path to the output PNG file
        compress: Whether to use compression (defaults to True)
    """
    # Parse EPS file
    bbox, commands = parse_eps_file(eps_file)
    
    # Calculate dimensions from bounding box
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    
    # Create interpreter and execute commands
    interpreter = SimplePostScriptInterpreter(width, height, bbox)
    bitmap = interpreter.execute(commands)
    
    # Encode as PNG
    encode_png(bitmap, png_file, compress=compress)
    
    print(f"Converted {eps_file} to {png_file}")
    print(f"Dimensions: {width}x{height} pixels")
    print(f"Bounding box: {bbox}")


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert EPS files to PNG')
    parser.add_argument('input', help='Input EPS file')
    parser.add_argument('output', help='Output PNG file')
    parser.add_argument('--no-compress', dest='compress', action='store_false',
                        help='Disable compression (produces larger files)')
    parser.set_defaults(compress=True)
    
    args = parser.parse_args()
    
    convert_eps_to_png(args.input, args.output, compress=args.compress)