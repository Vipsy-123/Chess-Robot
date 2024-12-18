''''
    1]This scipt take chessboard_centers.json file as Input and displays the respective file and rank on image of 640x640 pixels
    2]For e.g on Coordinate (40,40) it display a1

    Author : Vipul Pardeshi
'''

import cv2
import json

# Load the image
image = cv2.imread("../saved_files/board.png")
image = cv2.resize(image, (680, 680))

# Load the JSON file containing the center points
with open("../saved_files/chessboard_centers.json", "r") as json_file:
    centers = json.load(json_file)

# Define the font and font scale
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5

# Draw text on the image at the specified points
for key, center in centers.items():
    center_x, center_y = center
    text = key
    # Calculate the position to place the text
    text_offset_x = center_x - 10  # Adjust for text size
    text_offset_y = center_y + 10  # Adjust for text size
    cv2.putText(image, text, (text_offset_x, text_offset_y), font, font_scale, (0, 255, 0), 1, cv2.LINE_AA)

# Display the image with text
cv2.imshow("Chessboard with Text", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
