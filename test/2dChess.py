import chess
import chess.svg
import wand.image
import json
import cv2

# Load JSON data from file
with open('realworld_coordinates.json') as json_file:
    realworld_coords = json.load(json_file)

with open('predictions.json') as json_file2:
    predictions = json.load(json_file2)

# Mapping classes to piece name
class_mapping = {
    "1": "b", "2": "k", "3": "n", "4": "p", "5": "q", "6": "r",
    "7": "B", "8": "K", "9": "N", "10": "P", "11": "Q", "12": "R"
}

# Create an empty chess board
board = chess.Board(fen="8/8/8/8/8/8/8/8 w - - 0 1")

# Threshold for prediction of piece (in pixels)
thresh = 30

# Iterate through the predictions and update the board
for prediction in predictions["predictions"]:
    pred_x = prediction["x"]
    pred_y = prediction["y"]
    
    # Iterate through the squares and find the closest prediction
    for square, coord in realworld_coords.items():
        closest_prediction = None
        file_index = ord(square) - ord('a')  # Convert file to 0-indexed integer
        rank = -1
        for x, y in coord:
            rank += 1
            if (abs(pred_x - x) <= thresh and abs(pred_y - y) <= thresh):
                closest_prediction = prediction
                break
        
        # Ensure the file index and rank are within bounds
        if 0 <= file_index < 8 and 0 <= rank < 8:
            if closest_prediction:
                piece_name = class_mapping[closest_prediction["class"]]
                board.set_piece_at(chess.square(file_index, rank), chess.Piece.from_symbol(piece_name))
            # No need to set the square to None if there's no prediction
            # else:
            #     board.set_piece_at(chess.square(file_index, rank), None)

# Print the 2D board representation
print(board)

# Print the FEN string
print("FEN:", board.fen())

# Generate SVG representation of the board
board_svg = chess.svg.board(board=board, size=400, coordinates=False)

# Save the SVG to a temporary file
with open("chessboard.svg", "w") as svg_file:
    svg_file.write(board_svg)

# Convert SVG to PNG using wand
with wand.image.Image() as image:
    image.read(blob=board_svg.encode('utf-8'), format="svg")
    png_image = image.make_blob("png32")

# Save the PNG image
with open("chessboard.png", "wb") as out:
    out.write(png_image)

print("Chessboard images saved as chessboard.svg and chessboard.png")

# Load the saved image and display
img = cv2.imread("chessboard.png")
cv2.imshow('Board', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
