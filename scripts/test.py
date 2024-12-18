import chess
import chess.svg
import wand.image
import json
import cv2
import numpy as np
import os
import time
from typing import Dict, Tuple, Optional

class ChessboardProcessor :
    """
    A class to process chess moves based on known states and legal moves.
    """
    # Piece mapping dictionary
    PIECE_MAPPING = {
        "1": "b", "2": "k", "3": "n", "4": "p", "5": "q", "6": "r",
        "7": "B", "8": "K", "9": "N", "10": "P", "11": "Q", "12": "R"
    }
    
    def __init__(self, base_path: str = "../saved_files"):
        """
        Initialize the StatefulChessboardProcessor.
        
        Args:
            base_path (str): Base path for saved files
        """
        self.base_path = base_path
        self.centers_path = f"{base_path}/chessboard_centers.json"
        self.predictions_path = f"{base_path}/predictions.json"
        self.occupied_pos_path = f"{base_path}/occupied_positions.json"
        self.fen_path = f"{base_path}/fen.txt"
        self.svg_path = f"{base_path}/chessboard.svg"
        self.png_path = f"{base_path}/chessboard.png"
         # Class-level constants
        self.EMPTY_BOARD_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        
        self.board = chess.Board()  # Start with the standard chess configuration
        self.occupied_positions = self.initialize_occupied_positions_from_fen(self.EMPTY_BOARD_FEN)
    
    @staticmethod
    def _file_to_index(file: str) -> int:
        """Convert file letter to 0-indexed integer."""
        return ord(file) - ord('a')
    
    @staticmethod
    def _rank_to_index(rank: str) -> int:
        """Convert rank number to 0-indexed integer."""
        return int(rank) - 1
    
    @staticmethod
    def load_json_data(file_path: str) -> Dict:
        """Load JSON data from file with error handling."""
        try:
            with open(file_path) as json_file:
                return json.load(json_file)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading JSON from {file_path}: {e}")
            return {}
    
    def save_json_data(self, data: Dict, file_path: str) -> None:
        """Save JSON data to file."""
        with open(file_path, 'w') as file:
            json.dump(data, file)
    
    def save_string_to_file(self, string_data: str, file_path: str) -> None:
        """Save string data to file."""
        with open(file_path, 'w') as file:
            file.write(string_data)
    
    def find_closest_square(self, pred_x: float, pred_y: float, 
                           board_centers: Dict) -> Optional[str]:
        """Find the closest chess square for given coordinates."""
        for square, (square_x, square_y) in board_centers.items():
            if (abs(square_x - pred_x) <= self.PREDICTION_THRESHOLD and 
                abs(square_y - pred_y) <= self.PREDICTION_THRESHOLD):
                return square
        return None
    
    def initialize_occupied_positions_from_fen(self,fen: str) -> Dict[str, int]:
        """
        Initialize the occupied positions dictionary from a FEN string.

        Args:
            fen (str): The FEN string representing the chessboard state.

        Returns:
            Dict[str, int]: A dictionary mapping squares to 1 (occupied) or 0 (unoccupied).
        """
        occupied_positions = {f"{file}{rank}": 0 for file in 'abcdefgh' for rank in '12345678'}
        rows = fen.split()[0].split('/')  # Get the board rows from FEN
        
        # Iterate over the rows in reverse because FEN starts from rank 8
        for rank_idx, row in enumerate(reversed(rows)):
            file_idx = 0
            for char in row:
                if char.isdigit():
                    # Empty squares
                    file_idx += int(char)
                else:
                    # Occupied square
                    file = chr(ord('a') + file_idx)
                    rank = str(rank_idx + 1)
                    square = f"{file}{rank}"
                    occupied_positions[square] = 1
                    file_idx += 1
        
        return occupied_positions
    
    def update_board_from_predictions(self) -> None:
        """Update the chess board based on current predictions."""
        # Load latest data
        board_centers = self.load_json_data(self.centers_path)
        predictions = self.load_json_data(self.predictions_path)
        
        # Reset board and occupied positions
        self.board = chess.Board(fen=self.EMPTY_BOARD_FEN)
        self.occupied_positions = self._initialize_occupied_positions()
        
        # Process each prediction
        for prediction in predictions:
            pred_x = prediction["bounding_box"]["x"]
            pred_y = prediction["bounding_box"]["y"]
            
            closest_square = self.find_closest_square(pred_x, pred_y, board_centers)
            
            if closest_square:
                # Update board with piece
                file_idx = self._file_to_index(closest_square[0])
                rank_idx = self._rank_to_index(closest_square[1])
                piece_symbol = self.PIECE_MAPPING[prediction["class_name"]]
                piece = chess.Piece.from_symbol(piece_symbol)
                self.board.set_piece_at(chess.square(file_idx, rank_idx), piece)
                
                # Mark square as occupied
                self.occupied_positions[closest_square] = 1
    

    def save_board_state(self) -> None:
        """Save current board state to files."""
        # Save occupied positions
        self.save_json_data(self.occupied_positions, self.occupied_pos_path)
        
        # Save FEN string
        self.save_string_to_file(self.board.fen(), self.fen_path)

    def generate_board_visuals(self) -> None:
        """Generate and save visual representations of the board."""
        board_svg = chess.svg.board(board=self.board, size=400, coordinates=False)
        with open(self.svg_path, "w") as svg_file:
            svg_file.write(board_svg)
        with wand.image.Image() as image:
            image.read(blob=board_svg.encode('utf-8'), format="svg")
            png_image = image.make_blob("png32")
        with open(self.png_path, "wb") as out:
            out.write(png_image)

    def display_board(self) -> None:
        """Display the current board state."""
        img = cv2.imread(self.png_path)
        cv2.imshow('Board', img)
        cv2.waitKey(1000)

    def process_single_frame(self) -> None:
        """Simulate a single frame processing of moves."""
        try:
            # Example of updating board manually
            self.update_board_from_predictions()
            self.save_board_state()
            print("FEN:", self.board.fen())

            self.generate_board_visuals()
            self.display_board()
            # self.cleanup_temp_files()
        except Exception as e:
            print(f"Error processing frame: {e}")
        
    def run(self) -> None:
        """Main processing loop."""
        print("Starting chess board processing...")
        while True:
            try:
                self.process_single_frame()
                time.sleep(1)
            except KeyboardInterrupt:
                print("\nStopping chess board processing...")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(1)

def main():
    processor = ChessboardProcessor()
    processor.run()

if __name__ == "__main__":
    main()
