import os
import uuid
from PIL import Image

# Path to the source PNG file
source_file = "../saved_files/board.png"  # Replace with your file path

# Directory to save the images
output_dir = "saved_images"
os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist

try:
    # Open the source image
    with Image.open(source_file) as img:
        # Loop to save 10 unique copies
        for i in range(10):
            unique_id = uuid.uuid4()  # Generate a unique identifier
            output_file = os.path.join(output_dir, f"photo_{unique_id}.png")
            img.save(output_file, format="PNG")
            print(f"Saved: {output_file}")
except FileNotFoundError:
    print(f"Error: Source file '{source_file}' not found.")
except Exception as e:
    print(f"An error occurred: {e}")
