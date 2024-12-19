
import time
import json
import socket
import keyboard
import stockfish
import chess.engine
from typing import Tuple, Optional, Dict
import cv2
import chess
import chess.svg
import wand.image
import numpy as np
import os

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

class ChessGameState:
    """Enum-like class for chess game states"""
    NORMAL = "NORMAL"
    WHITE_IN_CHECK = "WHITE_IN_CHECK"
    BLACK_IN_CHECK = "BLACK_IN_CHECK"
    WHITE_CHECKMATE = "WHITE_CHECKMATE"
    BLACK_CHECKMATE = "BLACK_CHECKMATE"
    STALEMATE = "STALEMATE"
    DRAW = "DRAW"

class ChessPositionError(Exception):
    """Custom exception for invalid chess positions"""
    pass

class ChessRobotController:
    def __init__(self, 
                 stockfish_path=STOCKFISH_PATH, 
                 host='192.168.0.20', 
                 port=10002, 
                 ):
        self.robot_move = True
        self.human_move = False
        self.host = host
        self.port = port
        self.occupied_pos = self.load_json_data(OCCUPIED_POS_PATH)
        self.init_stockfish(stockfish_path)
        self.game_state = ChessGameState.NORMAL
        # Initialize chess board
        self.board = chess.Board()
        self.fen_string = self.board.fen()
        # Initialize chess engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        self.processor = ChessboardProcessor()

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
                    "UCI_Chess960": "false",
                    "MultiPV": 3  # Increased to get more move options for analysis
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
        
    def __del__(self):
        """Cleanup chess engine when object is destroyed"""
        if hasattr(self, 'engine'):
            self.engine.quit()

    def analyze_position(self, fen_string: str) -> Dict:
        """
        Analyze the current position for check, checkmate, and stalemate conditions
        using python-chess library.
        Returns a dictionary with position analysis.
        """
        try:
            # First check for game-ending states
            if self.check_game_ending_state(fen_string):
                return {'state': self.game_state}
            
            # Set up the position on our chess board
            self.board.set_fen(fen_string)
            
            # Initialize position info
            info = {}
            
            # Check for checkmate
            if self.board.is_checkmate():
                info['state'] = (ChessGameState.WHITE_CHECKMATE 
                               if self.board.turn == chess.WHITE 
                               else ChessGameState.BLACK_CHECKMATE)
                return info
            
            # Check for stalemate
            if self.board.is_stalemate():
                info['state'] = ChessGameState.STALEMATE
                return info
            
            # Check for draw
            if self.board.is_insufficient_material() or self.board.is_fifty_moves() or self.board.is_repetition():
                info['state'] = ChessGameState.DRAW
                return info
            
            # Check for check
            if self.board.is_check():
                info['state'] = (ChessGameState.WHITE_IN_CHECK 
                               if self.board.turn == chess.WHITE 
                               else ChessGameState.BLACK_IN_CHECK)
            else:
                info['state'] = ChessGameState.NORMAL
                
            return info
            
        except Exception as e:
            print(f"Error analyzing position: {e}")
            return {'state': ChessGameState.NORMAL}

    def get_best_move(self, fen_string: str) -> Tuple[Optional[str], Optional[str], Optional[bool]]:
        """Get best move using python-chess with enhanced error handling."""
        try:
            print("IN get moves")
            # First check game state
            if self.check_game_ending_state(fen_string):
                return None, None, None
            
            # Set up the position
            self.board.set_fen(fen_string)
            
            # Check if game is already over
            if self.board.is_game_over():
                return None, None, None
            
            # Get position analysis
            position_info = self.analyze_position(fen_string)
            self.game_state = position_info['state']
            self.display_game_state(self.game_state)
            
            # Check if game is over
            if self.game_state in [ChessGameState.WHITE_CHECKMATE, 
                                 ChessGameState.BLACK_CHECKMATE, 
                                 ChessGameState.STALEMATE, 
                                 ChessGameState.DRAW]:
                return None, None, None
            
            # Get best move from engine
            result = self.engine.play(self.board, chess.engine.Limit(time=2.0))
            if result.move is None:
                print("No legal moves available")
                return None, None, None
            
            # Convert move to string format
            move = result.move
            source = chess.square_name(move.from_square)
            destination = chess.square_name(move.to_square)
            
            # Check if destination square is occupied by checking for a list with color info
            is_attack = isinstance(self.occupied_pos.get(destination), list)

            return source, destination, is_attack
            
        except Exception as e:
            print(f"Error in get_best_move: {e}")
            return None, None, None
        
    def check_game_ending_state(self, fen_string: str) -> bool:
        """
        Check if the game has reached an ending state before FEN validation
        Returns True if game should end, False otherwise
        """
        try:
            position = fen_string.split()[0]
            
            # Check for kings
            piece_counts = {'K': 0, 'k': 0}
            for char in position:
                if char in piece_counts:
                    piece_counts[char] += 1
            
            # Check for missing kings
            if piece_counts['k'] == 0:
                self.game_state = ChessGameState.BLACK_CHECKMATE
                self.display_game_state(self.game_state)
                return True
                
            if piece_counts['K'] == 0:
                self.game_state = ChessGameState.WHITE_CHECKMATE
                self.display_game_state(self.game_state)
                return True
                
            return False
            
        except Exception as e:
            print(f"Error checking game state: {e}")
            return False

    def display_game_state(self, state: str) -> None:
        """Display the current game state with appropriate formatting"""
        state_messages = {
            ChessGameState.WHITE_IN_CHECK: "\n⚠️  WHITE KING IS IN CHECK! ⚠️\n",
            ChessGameState.BLACK_IN_CHECK: "\n⚠️  BLACK KING IS IN CHECK! ⚠️\n",
            ChessGameState.WHITE_CHECKMATE: "\n🏆  CHECKMATE! BLACK WINS! 🏆\n",
            ChessGameState.BLACK_CHECKMATE: "\n🏆  CHECKMATE! WHITE WINS! 🏆\n",
            ChessGameState.STALEMATE: "\n🤝  GAME DRAWN BY STALEMATE 🤝\n",
            ChessGameState.DRAW: "\n🤝  GAME DRAWN 🤝\n"
        }
        
        if state in state_messages:
            message = state_messages[state]
            border = "=" * (len(message) - 2)  # -2 for the newlines
            print(border)
            print(message, end='')
            print(border)

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


        
    def update_board_state(self, chance) -> None:
        """
        Update the chess board state and refresh all dependent game state information.
        
        This method handles:
        1. Getting new occupied positions
        2. Checking differences from previous state
        3. Updating the board state
        4. Refreshing the legal moves dictionary
        5. Updating the visual representation
        
        Args:
            chance: Boolean indicating whose turn it is (True for human, False for robot)
        """
        print("Starting board state update...")
        
        # Get new position information
        print("5.1: Getting new occupied positions")
        new_pos = self.processor.get_occupied_positions()
        
        print("5.2: Checking position differences")
        results = self.processor.diff_checker(
            self.occupied_pos, 
            new_pos,
            moves_dict=self.moves_dict,
            chance=chance
        )
        
        print("5.3: Updating occupied positions")
        self.occupied_pos = new_pos
        self.processor.save_json_data(self.occupied_pos,OCCUPIED_POS_PATH)
        

        # Update internal board state
        print("5.4: Updating board state")
        self.moves_dict, self.fen_string, self.board = self.processor.update_fen_from_occupied_pos(
            results=results, 
            moves_dict=self.moves_dict, 
            board=self.board,
            chance=chance
        )
        
        # Get fresh legal moves for the new position
        print("5.5: Refreshing legal moves dictionary")
        self.moves_dict = self.processor.get_legal_moves(self.fen_string)
        
        # Update visual representation
        print("5.6: Updating visual display")
        self.processor.board = self.board  # Sync processor's board with current state
        self.processor.generate_board_visuals()
        self.processor.display_board()

   
    def main(self):
        """Main game loop."""
        print("\n🎮 WELCOME TO CHESS ROBOT GAME 🎮")
        print("Press SPACE to start each turn...")
        
        
        
        while True:
            if keyboard.is_pressed('space'):
                self.occupied_pos = self.processor.get_occupied_positions()
                break
        while True:
                # Display the board and read FEN string
                self.processor.generate_board_visuals()
                self.processor.display_board()

                self.moves_dict = self.processor.get_legal_moves(self.fen_string)

                if self.fen_string is None:
                    print("❌ Error reading FEN string")
                    continue
                
                # Check for game-ending state first
                if self.check_game_ending_state(self.fen_string):
                    print("\n🏁 GAME OVER 🏁")
                    break
                
                # Check other game states (checkmate, stalemate, etc.)
                if self.game_state in [ChessGameState.WHITE_CHECKMATE, 
                                    ChessGameState.BLACK_CHECKMATE, 
                                    ChessGameState.STALEMATE, 
                                    ChessGameState.DRAW]:
                    print("\n🏁 GAME OVER 🏁")
                    break

                # HUMAN TURN
                if self.human_move:
                    print("\n👤 Human Player's Turn 👤")
                    print("Press SPACE when you've completed your move...")
                    
                    while True:
                        self.processor.generate_board_visuals()
                        self.processor.display_board()
                        if keyboard.is_pressed('space'):
                            time.sleep(3)
                            print("Processing move....")
                            self.robot_move = True
                            self.human_move = False
                            break
                        time.sleep(0.1)

                    # Update the board state after human's move
                    self.update_board_state(1)

                # ROBOT TURN
                if self.robot_move:
                    print("\n🤖 Robot's Turn 🤖")
                    try:
                        # Get best move and execute it
                        src, dst, is_attack = self.get_best_move(self.fen_string)

                        if src is None or dst is None:
                            print("Unable to make move, skipping robot's turn")
                            self.robot_move = True
                            self.human_move = False
                            return

                        # Send move to robot (through socket or other communication)
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((self.host, self.port))

                            attack = 1 if is_attack else 0

                            src_num = SQUARE_MAPPING[src]
                            dst_num = SQUARE_MAPPING[dst]
                            print(f"Robot moving from {src} --> {dst} ATTACK {attack}")
                            move_data = f'{src_num},{dst_num},{attack}'.encode()
                            s.sendall(move_data)

                            # Receive the response from the robot
                            response = s.recv(1024)
                            print('✅ Robot move successfully executed:', repr(response))

                            self.robot_move = False
                            self.human_move = True

                            time.sleep(2)

                            # Update board state after robot's move
                            self.update_board_state(0)

                    except socket.error as err:
                        print(f"❌ Socket error: {err}")
                    except Exception as e:
                        print(f"❌ Unexpected error during robot move: {e}")
                
                time.sleep(0.1)


def main():
    try:
        chess_controller = ChessRobotController()
        chess_controller.main()
    except KeyboardInterrupt as e:
        print(f"❌ GAME ENDED ❌")
        raise
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        raise

class ChessboardProcessor :
    """
    A class to process chess moves based on known states and legal moves.
    """
    # Piece mapping dictionary
    PIECE_MAPPING = {
        "1": "b", "2": "k", "3": "n", "4": "p", "5": "q", "6": "r",
        "7": "B", "8": "K", "9": "N", "10": "P", "11": "Q", "12": "R"
    }
    PREDICTION_THRESHOLD = 35
    
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
    
    def initialize_occupied_positions_from_fen(self, fen: str) -> Dict[str, list]:
        """
        Initialize the occupied positions dictionary from a FEN string.

        Args:
            fen (str): The FEN string representing the chessboard state.

        Returns:
            Dict[str, list]: A dictionary mapping squares to ["W", 1] (White occupied) or ["B", 1] (Black occupied),
                            or 0 (unoccupied).
        """
        # Initialize all squares as unoccupied (0)
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
                    
                    # Determine if the piece is White or Black
                    color = "W" if char.isupper() else "B"
                    occupied_positions[square] = [color, 1]
                    
                    file_idx += 1
        
        return occupied_positions

    
    def get_occupied_positions(self):
        """
        Generate a dictionary of occupied positions on the chessboard
        using the predictions and centers JSON files.
        
        Returns:
            dict: Dictionary with chessboard squares (e.g., 'a1') as keys
                  and 1 for occupied, 0 for unoccupied as values.
        """
        print("Occupied json updated")
        board_centers = self.load_json_data(self.centers_path)
        predictions = self.load_json_data(self.predictions_path)
        
        # Reset board and occupied positions
        # self.board = chess.Board(fen=self.EMPTY_BOARD_FEN)
        # self.occupied_positions = self._initialize_occupied_positions()
        occupied_positions = {}
        # Process each prediction
        for prediction in predictions:
            pred_x = prediction["bounding_box"]["x"]
            pred_y = prediction["bounding_box"]["y"]
            
            closest_square = self.find_closest_square(pred_x, pred_y, board_centers)
            
            if closest_square:

                # Mark square as occupied
                if int(prediction['class_name']) >= 7:
                    occupied_positions[closest_square] = ["W",1]
                elif int(prediction['class_name']) < 7:
                    occupied_positions[closest_square] = ["B",1]

        self.save_json_data(occupied_positions,self.occupied_pos_path)

        return occupied_positions


    def get_legal_moves(self, fen):
        """
        Extracts all legal moves for both white and black pieces regardless of whose turn it is.
        
        Args:
            fen (str): The FEN representation of the chessboard.
        
        Returns:
            dict: A dictionary containing legal moves for all pieces of both colors
        """
        print("Getting legal moves for both sides...")
        
        def get_moves_for_position(board):
            """Helper function to get moves for all pieces in a given position"""
            moves_by_piece = {}
            piece_counters = {'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0,
                            'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0}
            
            # First pass: count pieces and assign consistent IDs
            piece_positions = {}  # To store piece positions for consistent numbering
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    symbol = piece.symbol()
                    piece_counters[symbol] += 1
                    piece_id = f"{symbol}_{piece_counters[symbol]}"
                    piece_positions[piece_id] = square
            
            # Second pass: calculate legal moves for each piece
            saved_turn = board.turn  # Save current turn
            
            # Calculate moves for white pieces
            board.turn = chess.WHITE
            for piece_id, square in piece_positions.items():
                if piece_id[0].isupper():  # White pieces
                    moves = []
                    for move in board.legal_moves:
                        if move.from_square == square:
                            moves.append(chess.square_name(move.from_square) + 
                                    chess.square_name(move.to_square))
                    if moves:  # Only add pieces that have legal moves
                        moves_by_piece[piece_id] = moves
            
            # Calculate moves for black pieces
            board.turn = chess.BLACK
            for piece_id, square in piece_positions.items():
                if piece_id[0].islower():  # Black pieces
                    moves = []
                    for move in board.legal_moves:
                        if move.from_square == square:
                            moves.append(chess.square_name(move.from_square) + 
                                    chess.square_name(move.to_square))
                    if moves:  # Only add pieces that have legal moves
                        moves_by_piece[piece_id] = moves
            
            # Restore original turn
            board.turn = saved_turn
            return moves_by_piece

        try:
            # Create board from FEN
            board = chess.Board(fen)
            
            # Get all legal moves for both sides
            all_moves = get_moves_for_position(board)
            
            print(f"Calculated moves for both sides: {all_moves}")
            return all_moves
            
        except Exception as e:
            print(f"Error calculating legal moves: {e}")
            return {}

    def diff_checker(self, old_dict, new_dict, moves_dict, chance):
        """
        Compares two dictionaries to find changes in board state, specifically tracking
        squares that changed from occupied to unoccupied (source) and unoccupied to
        occupied (destination).

        Args:
            old_dict (dict): Previous board state with positions as {"square": ["color", occupancy]}
            new_dict (dict): Current board state with positions as {"square": ["color", occupancy]}
            moves_dict (dict): Dictionary of legal moves for each piece
            chance (bool): True for Human turn, False for Robot turn

        Returns:
            dict: Contains 'src' and 'dst' lists of affected squares
        """
        print("In Diff checker")

        def get_occupancy_value(value):
            """Extract occupancy value (0 or 1) from position data."""
            if isinstance(value, list):
                return value[1]
            return 0

        def get_color_value(value):
            """Extract color value ('W' or 'B') from position data."""
            if isinstance(value, list):
                return value[0]
            return None

        # Find source squares (where pieces moved from)
        src_squares = []
        for square, old_value in old_dict.items():
            # Check if square was occupied before and is now empty
            if (get_occupancy_value(old_value) == 1 and 
                get_occupancy_value(new_dict.get(square, 0)) == 0):
                src_squares.append(square)

        # Find destination squares (where pieces moved to)
        dst_squares = []
        for square, new_value in new_dict.items():
            # A square is a destination if:
            # 1. It is now occupied (new_value[1] == 1)
            # 2. It was either empty before (old_value[1] == 0) or contains a captured piece
            old_value = old_dict.get(square, 0)
            if get_occupancy_value(new_value) == 1:
                old_occupancy = get_occupancy_value(old_value)
                if old_occupancy == 0:
                    # Simple move to empty square
                    dst_squares.append(square)
                else:
                    # Potential capture - verify based on color change
                    old_color = get_color_value(old_value)
                    new_color = get_color_value(new_value)
                    if ((chance and old_color == "W" and new_color == "B") or  # Human captures White
                        (not chance and old_color == "B" and new_color == "W")):  # Robot captures Black
                        dst_squares.append(square)

        # Validate moves against legal moves dictionary
        validated_dst = []
        for dst in dst_squares:
            for moves in moves_dict.values():
                # Check if any source square can legally move to this destination
                if any(move[2:4] == dst and move[:2] in src_squares for move in moves):
                    validated_dst.append(dst)
                    break

        results = {
            "src": src_squares,
            "dst": list(set(validated_dst))  # Remove any duplicates
        }
        
        print(f"Detected changes - Source: {results['src']}, Destination: {results['dst']}")
        return results


    # Function to convert file to 0-indexed integer
    def file_to_index(self,file):
        return ord(file) - ord('a')

    # Function to convert rank to 0-indexed integer
    def rank_to_index(self,rank):
        return int(rank) - 1

    def update_fen_from_occupied_pos(self, results, moves_dict, board, chance):
        """
        Update the chess board state and moves dictionary based on detected moves and captures.
        
        Args:
            results (dict): Dictionary containing source, destination squares
            moves_dict (dict): Dictionary of legal moves for pieces
            board (chess.Board): Current chess board state
            chance (bool): True for Human turn, False for Robot turn
        
        Returns:
            tuple: Updated moves_dict, FEN string, and board
        """
        try:
            print("Processing move results...")
            print(results)

            src = results.get("src", [None])[0]
            dst = results.get("dst", [None])[0]

            if src is None or dst is None:
                print(" 🚨 WARNING: Source or Destination square is missing. 🚨")
                return moves_dict, board.fen(), board

            move = src + dst
            print(f"Move determined: {move}")

            # Find the piece making the move
            piece_symbol = None
            matching_piece = None
            for piece, moves in moves_dict.items():
                if move in moves:
                    piece_symbol = piece[0]
                    matching_piece = piece
                    break

            if not matching_piece:
                print(f"🚨 WARNING: No legal move found for {move} 🚨")
                return moves_dict, board.fen(), board

            print(f"Moving PIECE: {piece_symbol} from {src} to {dst}")

            # Convert squares to board indices
            src_square = chess.parse_square(src)
            dst_square = chess.parse_square(dst)
            
            # Create and validate the move
            move_obj = chess.Move(src_square, dst_square)
            if move_obj not in board.legal_moves:
                print(f"🚨 WARNING: Illegal move attempted: {move} 🚨")
                return moves_dict, board.fen(), board

            # Make the move on the board
            board.push(move_obj)

            # Update turn in FEN string
            if chance:  # Human's turn
                fen_parts = board.fen().split()
                fen_parts[1] = 'w'  # Set to white's turn
                new_fen = ' '.join(fen_parts)
                board.set_fen(new_fen)
            else:  # Robot's turn
                fen_parts = board.fen().split()
                fen_parts[1] = 'b'  # Set to black's turn
                new_fen = ' '.join(fen_parts)
                board.set_fen(new_fen)

            # Initialize piece counters for both colors
            piece_counters = {'P': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0,
                            'p': 0, 'n': 0, 'b': 0, 'r': 0, 'q': 0, 'k': 0}
            
            # Create new moves dictionary
            updated_moves_dict = {}
            
            # Calculate legal moves for both colors
            for square in chess.SQUARES:
                piece = board.piece_at(square)
                if piece:
                    symbol = piece.symbol()
                    piece_counters[symbol] += 1
                    piece_id = f"{symbol}_{piece_counters[symbol]}"
                    
                    # Calculate legal moves for this piece
                    legal_moves = []
                    for move in board.legal_moves:
                        if move.from_square == square:
                            legal_moves.append(
                                chess.square_name(move.from_square) + 
                                chess.square_name(move.to_square)
                            )
                    
                    # Only add if the piece has legal moves
                    if legal_moves:
                        updated_moves_dict[piece_id] = legal_moves

            print(f"Updated Moves Dictionary: {updated_moves_dict}")
            print(f"New FEN string: {board.fen()}")

            return updated_moves_dict, board.fen(), board
                
        except Exception as e:
            print(f"❌ Error updating board state: {e}")
            return moves_dict, board.fen(), board
        
    def save_board_state(self) -> None:
        """Save current board state to files."""
        # Save occupied positions
        self.save_json_data(self.occupied_positions, self.occupied_pos_path)
        
        # Save FEN string
        self.save_string_to_file(self.board.fen(), self.fen_path)

    def generate_board_visuals(self) -> None:
        """Generate and save visual representations of the board with proper cleanup."""
        # Generate SVG
        board_svg = chess.svg.board(board=self.board, size=400, coordinates=False)
        
        # Save SVG with proper cleanup
        with open(self.svg_path, "w") as svg_file:
            svg_file.write(board_svg)
        
        # Convert to PNG with proper resource handling
        with wand.image.Image() as image:
            image.read(blob=board_svg.encode('utf-8'), format="svg")
            png_image = image.make_blob("png32")
            with open(self.png_path, "wb") as out:
                out.write(png_image)
        
        # Ensure files are properly closed and resources released
        # cv2.destroyAllWindows()

    def display_board(self) -> None:
        """Display the current board state with proper window handling."""
        # Read the latest PNG
        img = cv2.imread(self.png_path)
        if img is not None:
            cv2.imshow('Actual Board', img)
            cv2.waitKey(1)  # Short delay to allow window to update
        else:
            print("Warning: Failed to load board image")


if __name__ == '__main__':
    main()

