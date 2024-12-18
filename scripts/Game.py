import os
import time
import json
import socket
import keyboard
import stockfish
import chess.engine
from typing import Tuple, Optional, Dict

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
                 port=10002):
        self.robot_move = True
        self.human_move = False
        self.host = host
        self.port = port
        self.occupied_pos = self.load_json_data(OCCUPIED_POS_PATH)
        self.init_stockfish(stockfish_path)
        self.game_state = ChessGameState.NORMAL
        # Initialize chess board
        self.board = chess.Board()
        # Initialize chess engine
        self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)

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
            
            return source, destination, False
            
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

    # def analyze_position(self, fen_string: str) -> Dict:
    #     """
    #     Analyze the current position for check, checkmate, and stalemate conditions.
    #     Uses Stockfish's built-in check detection.
    #     Returns a dictionary with position analysis.
    #     """
    #     try:
    #         # First check for game-ending states
    #         if self.check_game_ending_state(fen_string):
    #             return {'state': self.game_state}
            
    #         self.stockfish.set_fen_position(fen_string)
            
    #         # Get evaluation from Stockfish
    #         evaluation = self.stockfish.get_evaluation()
    #         is_mate = evaluation['type'] == 'mate'
            
    #         # Parse FEN to determine whose turn it is
    #         turn = fen_string.split()[1]
    #         white_to_move = turn == 'w'
            
    #         # Get legal moves
    #         legal_moves = self.stockfish.get_top_moves(1)
    #         has_legal_moves = len(legal_moves) > 0
            
    #         # Initialize position info
    #         info = {}
            
    #         # Check for checkmate
    #         if is_mate and evaluation['value'] == 0:
    #             info['state'] = ChessGameState.WHITE_CHECKMATE if white_to_move else ChessGameState.BLACK_CHECKMATE
    #             return info
            
    #         # Check for stalemate
    #         if not has_legal_moves and not is_mate:
    #             info['state'] = ChessGameState.STALEMATE
    #             return info
            
    #         # Use Stockfish's built-in check detection
    #         is_in_check = self.stockfish.is_check()
            
    #         if is_in_check:
    #             info['state'] = ChessGameState.WHITE_IN_CHECK if white_to_move else ChessGameState.BLACK_IN_CHECK
    #         else:
    #             info['state'] = ChessGameState.NORMAL
                
    #         return info
            
    #     except Exception as e:
    #         print(f"Error analyzing position: {e}")
    #         return {'state': ChessGameState.NORMAL}

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

    # def get_best_move(self, fen_string: str) -> Tuple[Optional[str], Optional[str], Optional[bool]]:
    #     """Get best move using Stockfish with enhanced error handling."""
    #     try:
    #         # First check game state
    #         if self.check_game_ending_state(fen_string):
    #             return None, None, None
            
    #         # Then validate FEN
    #         if not self.validate_fen(fen_string):
    #             raise ChessPositionError("Invalid chess position")
            
    #         # Analyze position
    #         position_info = self.analyze_position(fen_string)
    #         self.game_state = position_info['state']
    #         self.display_game_state(self.game_state)
            
    #         # Check if game is over
    #         if self.game_state in [ChessGameState.WHITE_CHECKMATE, 
    #                              ChessGameState.BLACK_CHECKMATE, 
    #                              ChessGameState.STALEMATE, 
    #                              ChessGameState.DRAW]:
    #             return None, None, None
            
    #         # Get best move
    #         best_move = self.stockfish.get_best_move()
    #         if not best_move:
    #             print("No legal moves available")
    #             return None, None, None
            
    #         source = best_move[:2]
    #         destination = best_move[2:4]
    #         return source, destination, False
            
    #     except ChessPositionError as e:
    #         print(f"Chess position error: {e}")
    #         return None, None, None
    #     except Exception as e:
    #         print(f"Error in get_best_move: {e}")
    #         return None, None, None

    def play(self, fen_string: str) -> None:
        """Main game play logic with enhanced error handling."""
        if self.robot_move:
            print("\n🤖 Robot's Turn 🤖")
            try:
                # Get best move with error handling
                src, dst, _ = self.get_best_move(fen_string)
                
                if src is None or dst is None:
                    print("Unable to make move, skipping robot's turn")
                    self.robot_move = True
                    self.human_move = False
                    return
                
                # Connect to robot and send move
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    
                   
                    
                    if self.occupied_pos.get(dst) == 1 : attk = 1
                    else : attk = 0

                    src_num = SQUARE_MAPPING[src]
                    dst_num = SQUARE_MAPPING[dst]
                    
                    print(f"Robot moving from {src} --> {dst} ATTACK {attk}")
                    move_data = f'{src_num},{dst_num},{attk}'.encode()
                    s.sendall(move_data)
                    
                    response = s.recv(1024)
                    print('✅ Robot move successfully executed:', repr(response))
                    
                    self.robot_move = False
                    self.human_move = True
                    time.sleep(3)
            
            except socket.error as err:
                print(f"❌ Socket error: {err}")
            except Exception as e:
                print(f"❌ Unexpected error during robot move: {e}")

        if self.human_move:
            print("\n👤 Human Player's Turn 👤")
            print("Press SPACE when you've completed your move...")
            while True:
                if keyboard.is_pressed('space'):
                    self.robot_move = True
                    self.human_move = False
                    break
                time.sleep(0.1)

    def main(self):
        """Main game loop."""
        print("\n🎮 WELCOME TO CHESS ROBOT GAME 🎮")
        print("Press SPACE to start each turn...")
        
        while True:
            # Read FEN string
            fen_string = self.read_string_from_file(FEN_FILE_PATH)
            
            if fen_string is None:
                print("❌ Error reading FEN string")
                continue
            
            # Check for game-ending state first
            if self.check_game_ending_state(fen_string):
                print("\n🏁 GAME OVER 🏁")
                break
            
            # Check other game states
            if self.game_state in [ChessGameState.WHITE_CHECKMATE, 
                                 ChessGameState.BLACK_CHECKMATE, 
                                 ChessGameState.STALEMATE, 
                                 ChessGameState.DRAW]:
                print("\n🏁 GAME OVER 🏁")
                break
                
            # Wait for space key
            if keyboard.is_pressed('space'):
                print("✨ Turn started!")
                self.play(fen_string)
            
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

if __name__ == '__main__':
    main()