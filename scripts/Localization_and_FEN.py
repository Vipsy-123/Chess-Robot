''' 
Code Description:

1] This script continuously processes predictions from the updated JSON file and updates a virtual chessboard with detected pieces.
2] It uses the predictions to update the FEN representation of the board, generates SVG and PNG images of the updated board, and displays the PNG image.
3] The script runs in a while loop until interrupted by the user (Ctrl+C).
4] It reads the updated predictions.json file in each iteration to ensure continuous processing.

'''

import chess
import chess.svg
import wand.image
import json
import cv2
import numpy as np
import os
import time

# Function to convert file to 0-indexed integer
def file_to_index(file):
    return ord(file) - ord('a')

# Function to convert rank to 0-indexed integer
def rank_to_index(rank):
    return int(rank) - 1

# Function to load JSON data from file
def load_json_data(file_path):
    with open(file_path) as json_file:
        return json.load(json_file)

def save_string_to_file(filename, string_to_save):
    with open(filename, 'w') as file:
        file.write(string_to_save)

# Define file paths
chessboard_centers_path = '../saved_files/chessboard_centers.json'
predictions_path = '../saved_files/predictions.json'

# Mapping classes to piece name
class_mapping = {
    "1": "b", "2": "k", "3": "n", "4": "p", "5": "q", "6": "r",
    "7": "B", "8": "K", "9": "N", "10": "P", "11": "Q", "12": "R"
}

# Threshold for prediction of piece (in pixels)
thresh = 35 # Adjusted threshold
while True:
    try:
    # Continuous processing until interrupted
    
        # Load JSON data from files
        board_centers = load_json_data(chessboard_centers_path)
        predictions = load_json_data(predictions_path)

        # Create an empty chess board
        board = chess.Board(fen="8/8/8/8/8/8/8/8 w - - 0 1")

        # Iterate through the predictions and update the board
        for prediction in predictions:
            pred_x = prediction["bounding_box"]["x"]
            pred_y = prediction["bounding_box"]["y"]
            closest_square = None
            in_box = False

            # Iterate over all Chessboard center coordinates to find the perfect match for the selected prediction
            for square, coord in board_centers.items():
                square_x, square_y = coord
                # If predicted coordinate falls in a box within +- 35 px of Chessboard center we got the match
                if(abs(square_x - pred_x) <= thresh and abs(square_y - pred_y) <=thresh):
                    in_box = True
                    closest_square = square
                    break

            # Ensure a closest square is found
            if closest_square and in_box :  # Added condition for threshold
                file_index = file_to_index(closest_square[0])  # Convert file to 0-indexed integer
                rank = rank_to_index(closest_square[1])  # Convert rank to 0-indexed integer
                piece_name = class_mapping[prediction["class_name"]]
                board.set_piece_at(chess.square(file_index, rank), chess.Piece.from_symbol(piece_name))

        # Save FEN string to a file for later usage
        fen_string = board.fen()
        filename = "../saved_files/fen.txt"
        save_string_to_file(filename, fen_string)

        # Print the FEN string
        print("FEN:", fen_string)

        # Generate SVG representation of the board
        board_svg = chess.svg.board(board=board, size=400, coordinates=False)

        # Save the SVG to a temporary file
        with open("../saved_files/chessboard.svg", "w") as svg_file:
            svg_file.write(board_svg)

        # Convert SVG to PNG using wand
        with wand.image.Image() as image:
            image.read(blob=board_svg.encode('utf-8'), format="svg")
            png_image = image.make_blob("png32")

        # Save the PNG image
        with open("../saved_files/chessboard.png", "wb") as out:
            out.write(png_image)

        print("Chessboard images saved as chessboard.svg and chessboard.png")

        # Load the saved image and display
        img = cv2.imread("../saved_files/chessboard.png")
        cv2.imshow('Board', img)
        cv2.waitKey(1000)  # Display for 1 second
        # cv2.destroyAllWindows()
        
        # Remove temporary files
        os.remove("../saved_files/chessboard.svg")
        os.remove("../saved_files/chessboard.png")

    except Exception as e:
        ("Error:", e)
        # print("Image not available. Retrying in a second...")

        time.sleep(1)
        continue
