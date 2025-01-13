import os
import time
import json
import socket
import keyboard
import stockfish
from typing import Tuple, Optional

# Global configuration remains the same
OCCUPIED_POS_PATH = '../saved_files/occupied_positions.json'
FEN_FILE_PATH = "../saved_files/fen.txt"
STOCKFISH_PATH = "./stockfish/stockfish-windows-x86-64-avx2.exe"

# Square mapping remains the same
SQUARE_MAPPING = {
    'a1': 1, 'a2': 2, 'a3': 3, 'a4': 4, 'a5': 5, 'a6': 6, 'a7': 7, 'a8': 8,
    'b1': 9, 'b2': 10, 'b3': 11, 'b4': 12, 'b5': 13, 'b6': 14, 'b7': 15, 'b8': 16,
    'c1': 17, 'c2': 18, 'c3': 19, 'c4': 20, 'c5': 21, 'c6': 22, 'c7': 23, 'c8': 24,
    'd1': 25, 'd2': 26, 'd3': 27, 'd4': 28, 'd5': 29, 'd6': 30, 'd7': 31, 'd8': 32,
    'e1': 33, 'e2': 34, 'e3': 35, 'e4': 36, 'e5': 37, 'e6': 38, 'e7': 39, 'e8': 40,
    'f1': 41, 'f2': 42, 'f3': 43, 'f4': 44, 'f5': 45, 'f6': 46, 'f7': 47, 'f8': 48,
    'g1': 49, 'g2': 50, 'g3': 51, 'g4': 52, 'g5': 53, 'g6': 54, 'g7': 55, 'g8': 56,
    'h1': 57, 'h2': 58, 'h3': 59, 'h4': 60, 'h5': 61, 'h6': 62, 'h7': 63, 'h8': 64
}


class ChessPositionError(Exception):
    """Custom exception for invalid chess positions"""
    pass

class ChessRobotController:
    def __init__(self, 
                 stockfish_path=STOCKFISH_PATH, 
                 host='192.168.0.20', 
                 port=10002):
        self.robot_move = True
        self.human_move = False
        self.host = host
        self.port = port
        self.occupied_pos = self.load_json_data(OCCUPIED_POS_PATH)
        self.init_stockfish(stockfish_path)
    
    def validate_fen(self, fen_string: str) -> bool:
        """
        Validate FEN string for common errors.
        Returns True if valid, False otherwise.
        """
        try:
            # Split FEN into its components
            parts = fen_string.split()
            if len(parts) != 6:
                print("Invalid FEN: Wrong number of fields")
                return False
            
            position = parts[0]
            
            # Check for presence of kings
            if 'K' not in position or 'k' not in position:
                print("Invalid FEN: Missing king(s)")
                return False
            
            # Check for valid piece counts
            piece_counts = {'K': 0, 'k': 0}
            for char in position:
                if char in piece_counts:
                    piece_counts[char] += 1
            
            if piece_counts['K'] != 1 : 
                print("BLACK TEAM WINS !")
                return False
            if piece_counts['k'] != 1:
                print("WHITE TEAM WINS !")
                return False
            
            # Validate board structure
            ranks = position.split('/')
            if len(ranks) != 8:
                print("Invalid FEN: Wrong number of ranks")
                return False
            
            for rank in ranks:
                space_count = 0
                for char in rank:
                    if char.isdigit():
                        space_count += int(char)
                    else:
                        space_count += 1
                if space_count != 8:
                    print("Invalid FEN: Invalid rank length")
                    return False
            
            return True
            
        except Exception as e:
            print(f"FEN validation error: {e}")
            return False

    def init_stockfish(self, stockfish_path: str) -> None:
        """Initialize Stockfish engine with enhanced error handling."""
        try:
            if not os.path.exists(stockfish_path):
                raise FileNotFoundError(f"Stockfish not found at {stockfish_path}")
            
            self.stockfish = stockfish.Stockfish(
                path=stockfish_path,
                depth=15,
                parameters={
                    "Threads": min(4, os.cpu_count()),
                    "Hash": 128,
                    "Skill Level": 20,
                    "UCI_Chess960": "false",  # Disable Chess960 for standard chess
                    "MultiPV": 1  # Single best move
                }
            )
        except Exception as e:
            print(f"Stockfish initialization error: {e}")
            raise
    
    @staticmethod
    def load_json_data(file_path):
        """Load JSON data with error handling."""
        try:
            with open(file_path) as json_file:
                return json.load(json_file)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading JSON from {file_path}: {e}")
            return {}
    
    @staticmethod
    def read_string_from_file(filename):
        """Read string from file with error handling."""
        try:
            with open(filename, 'r') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return None
        
    def get_best_move(self, fen_string: str) -> Tuple[Optional[str], Optional[str], Optional[bool]]:
        """Get best move using Stockfish with enhanced error handling."""
        try:
            # Validate FEN string first
            if not self.validate_fen(fen_string):
                raise ChessPositionError("Invalid chess position")
            
            # Check if position is legal
            if not self.stockfish.is_fen_valid(fen_string):
                raise ChessPositionError("Stockfish reports invalid position")
            
            # Set position and verify it was set correctly
            self.stockfish.set_fen_position(fen_string)
            current_fen = self.stockfish.get_fen_position()
            if current_fen != fen_string:
                raise ChessPositionError("Failed to set position correctly")
            
            # Check if game is over
            if self.stockfish.get_evaluation()['type'] == 'mate' and self.stockfish.get_evaluation()['value'] == 0:
                print("Game is already in checkmate")
                return None, None, None
            
            # Get best move
            best_move = self.stockfish.get_best_move()
            if not best_move:
                print("No legal moves available")
                return None, None, None
            
            source = best_move[:2]
            destination = best_move[2:4]
            return source, destination, False
            
        except ChessPositionError as e:
            print(f"Chess position error: {e}")
            return None, None, None
        except Exception as e:
            print(f"Error in get_best_move: {e}")
            return None, None, None

    def play(self, fen_string: str) -> None:
        """Main game play logic with enhanced error handling."""
        if self.robot_move:
            print("Robot's Chance")
            try:
                # Get best move with error handling
                src, dst, _ = self.get_best_move(fen_string)
                
                if src is None or dst is None:
                    print("Unable to make move, skipping robot's turn")
                    self.robot_move = False
                    self.human_move = True
                    return
                
                # Connect to robot and send move
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    # s.settimeout(30.0)  # Add timeout
                    s.connect((self.host, self.port))
                    
                    print(f"Robot moving from {src} --> {dst}")
                    attk = 1 if self.occupied_pos.get(dst, 0) == 1 else 0
                    src_num = SQUARE_MAPPING[src]
                    dst_num = SQUARE_MAPPING[dst]
                    
                    move_data = f'{src_num},{dst_num},{attk}'.encode()
                    s.sendall(move_data)
                    
                    response = s.recv(1024)
                    print('Robot move successfully executed:', repr(response))
                    
                    self.robot_move = False
                    self.human_move = True
                    time.sleep(2)
            
            except socket.error as err:
                print(f"Socket error: {err}")
                # Don't change turns if robot move failed
            except Exception as e:
                print(f"Unexpected error during robot move: {e}")
                # Don't change turns if robot move failed

        if self.human_move:
            print("Human Player's Chance")
            while True:
                if keyboard.is_pressed('space'):
                    self.robot_move = True
                    self.human_move = False
                    break
                time.sleep(0.1)

    def main(self):
        """Main game loop."""
        print("WELCOME TO CHESS ROBOT GAME")
        print("PRESS SPACE TO CONTINUE")
        
        while True:
            # Read FEN string
            fen_string = self.read_string_from_file(FEN_FILE_PATH)
            
            if fen_string is None:
                print("Error reading FEN string")
                continue
            
            # Wait for space key
            if keyboard.is_pressed('space'):
                print("Key pressed!")
                self.play(fen_string)
            
            # Optional: Add a small delay to prevent high CPU usage
            time.sleep(0.1)

def main():
    try:
        chess_controller = ChessRobotController()
        chess_controller.main()
    except Exception as e:
        print(f"Fatal error: {e}")
        # Optionally add logging here
        raise

if __name__ == '__main__':
    main()