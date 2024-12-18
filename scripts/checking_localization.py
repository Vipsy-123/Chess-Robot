import cv2
import json

# Load the image
image = cv2.imread("../saved_files/board.png")
image = cv2.resize(image, (680, 680))

# Load the JSON file containing the center points for the chessboard squares
with open("../saved_files/chessboard_centers.json", "r") as json_file:
    centers = json.load(json_file)

# Load the JSON file with bounding boxes and detection information
with open("../saved_files/predictions.json", "r") as json_file:
    detections = json.load(json_file)

# Define the font and font scale for displaying ranks/files on the image
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5

# Draw green text for chessboard square identifiers
for key, center in centers.items():
    center_x, center_y = center
    text = key
    # Calculate the position to place the text
    text_offset_x = center_x - 10  # Adjust for text size
    text_offset_y = center_y + 10  # Adjust for text size
    cv2.putText(image, text, (text_offset_x, text_offset_y), font, font_scale, (0, 255, 0), 1, cv2.LINE_AA)

# Draw the names of chess pieces from bounding boxes
for detection in detections:
    # Extract bounding box data
    bbox = detection['bounding_box']
    x = bbox['x']
    y = bbox['y']
    width = bbox['width']
    height = bbox['height']
    
    # Calculate the center of the bounding box
    center_x = int(x)
    center_y = int(y)
    
    # Get the chess piece name from the detection data
    piece_name = detection['class_name']
    
    # Draw the piece name at the center of the bounding box
    text_offset_x = center_x - 20  # Adjust for text size and centering
    text_offset_y = center_y + 10  # Adjust for text size
    cv2.putText(image, piece_name, (text_offset_x, text_offset_y), font, font_scale, (0, 0, 255), 1, cv2.LINE_AA)  # Red text

# Display the image with text and piece names
cv2.imshow("Chessboard with Pieces and Text", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
