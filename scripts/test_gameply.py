
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
import os
from enum import Enum
import logging
import os

# Ensure the 'logs' directory exists
log_directory = './logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create file handler for logging to file
file_handler = logging.FileHandler(f'{log_directory}/debug.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add file handler to logger
logger.addHandler(file_handler)

# (Optional) Create console handler for logging to console (set level to INFO or higher)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Optional: Only log INFO and higher to console
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

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

PLAYSTATE_MAPPING = {
    0 : "SETUP",
    1 : "ROBOT_PLAYING",
    2 : "ROBOT_COMM_COMPLETE",
    3 : "ROBOT_PLAYING_DONE",
    4 : "HUMAN_PLAYING",
    5 : "HUMAN_COMM_COMPLETE",
    6 : "HUMAN_PLAYING_DONE" 
}

class ChessGameState:
    """Enum-like class for chess game states"""
    NORMAL = "NORMAL"
    RETRY = "RETRY"
    WHITE_IN_CHECK = "WHITE_IN_CHECK"
    BLACK_IN_CHECK = "BLACK_IN_CHECK"
    WHITE_CHECKMATE = "WHITE_CHECKMATE"
    BLACK_CHECKMATE = "BLACK_CHECKMATE"
    STALEMATE = "STALEMATE"
    DRAW = "DRAW"

class PlayState(Enum):
    SETUP = 0
    ROBOT_PLAYING = 1
    ROBOT_COMM_COMPLETE = 2
    ROBOT_PLAYING_DONE = 3
    HUMAN_PLAYING = 4
    HUMAN_COMM_COMPLETE = 5
    HUMAN_PLAYING_DONE = 6

class ChessPositionError(Exception):
    """Custom exception for invalid chess positions"""
    pass

class ChessRobotController:

    # Move type constants
    SIMPLE_MOVE = 0
    ATTACK_MOVE = 1
    CASTLING_KS_MOVE = 2
    CASTLING_QS_MOVE = 3


    def __init__(self, 
                 stockfish_path=STOCKFISH_PATH, 
                 host='192.168.0.20', 
                 port=10002,
                 fen_string = None, 
                 move = "R",
                 ps = PlayState.SETUP.value
                 ):
        
        self.host = host
        self.port = port
        self.occupied_pos = self.load_json_data(OCCUPIED_POS_PATH)
        self.init_stockfish(stockfish_path)
        self.game_state = ChessGameState.NORMAL
        self.play_state = PlayState.SETUP.value
        self.src = None
        self.dst = None

        # Initialize chess board
        if fen_string is None :
            logger.info("Initialising FEN and Board")
            self.board = chess.Board()
            self.board.set_castling_fen("-")
            self.fen_string = self.board.fen()
            
        else:
            logger.info("Re-initialising FEN and Board")
            self.fen_string = fen_string
            self.board = chess.Board(fen=self.fen_string)
            self.game_state = ChessGameState.RETRY
            self.play_state = ps
        
        if move == "R":
            logger.info("Init Robot Move")
            self.robot_move = True
            self.human_move = False
        elif move == "H":
            logger.info("Init Human Move")
            self.robot_move = False
            self.human_move = True

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
            logger.error(f"Stockfish initialization error: {e}")
            raise
    
    @staticmethod
    def load_json_data(file_path):
        """Load JSON data with error handling."""
        try:
            with open(file_path) as json_file:
                return json.load(json_file)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading JSON from {file_path}: {e}")
            return {}
    
    @staticmethod
    def read_string_from_file(filename):
        """Read string from file with error handling."""
        try:
            with open(filename, 'r') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
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
            logger.info(f"Error analyzing position: {e}")
            return {'state': ChessGameState.NORMAL}

    def get_best_move(self, fen_string: str) -> Tuple[Optional[str], Optional[str], Optional[int]]:
        """Get best move using python-chess with enhanced error handling and move type detection."""
        try:
            logger.info("Getting Best moves")
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
                logger.error(f"❌ ERROR : GET_BEST_MOVE --> Engine Failed to get best moves ❌")
                error_handler(fen_string=self.fen_string,state=self.play_state)
                logger.info("🚨Quiting🚨")
                exit(0)
            
            # Convert move to string format
            move = result.move
            source = chess.square_name(move.from_square)
            destination = chess.square_name(move.to_square)
            
            # Determine move type
            move_type = self.SIMPLE_MOVE  # Default to simple move

            # Check if move is castling
            # fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1"
            board = chess.Board(self.fen_string)
            ks_castling,qs_castling = self.check_white_castling_availability(board)

            # Check if move is an attack
            if ks_castling:
                logger.info("KS Castling")
                move_type = self.CASTLING_KS_MOVE
            elif qs_castling:
                logger.info("QS Castling")
                move_type = self.CASTLING_QS_MOVE
            elif isinstance(self.occupied_pos.get(destination), list):
                move_type = self.ATTACK_MOVE

            return source, destination, move_type
            
        except Exception as e:
            logger.error(f"❌ ERROR : GET_BEST_MOVE -->  {e}")
            error_handler(fen_string=self.fen_string,state=self.play_state)
            logger.info("🚨Quiting🚨")
            exit(0)
            
            # return None, None, None
    

    def check_white_castling_availability(self, board):
        # logger.info("Castling Checkkk")
        logger.info(self.fen_string)

        # Check if White has kingside castling rights
        can_castle_kingside = board.has_kingside_castling_rights(chess.WHITE)

        # Check if the squares F1 and G1 are empty for kingside castling
        ks_clear = self.occupied_pos.get("f1", 0) == 0 and self.occupied_pos.get("g1", 0) == 0

        # Check if White has queenside castling rights
        can_castle_queenside = board.has_queenside_castling_rights(chess.WHITE)

        # Check if the squares B1, C1, and D1 are empty for queenside castling
        qs_clear = self.occupied_pos.get("b1", 0) == 0 and self.occupied_pos.get("c1", 0) == 0 and self.occupied_pos.get("d1", 0) == 0

        # logger.info the results for debugging
        # logger.info(f"Kingside castling: {can_castle_kingside and ks_clear}")
        # logger.info(f"Queenside castling: {can_castle_queenside and qs_clear}")

        # Return the availability of castling
        return (can_castle_kingside and ks_clear), (can_castle_queenside and qs_clear)

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
            logger.error(f"Error checking game state: {e}")
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
            logger.info(border)
            logger.info(message)
            logger.info(border)

    def validate_fen(self, fen_string: str) -> bool:
        """
        Validate FEN string for common errors.
        Returns True if valid, False otherwise.
        """
        try:
            # Split FEN into its components
            parts = fen_string.split()
            if len(parts) != 6:
                logger.warning("Invalid FEN: Wrong number of fields")
                return False
            
            position = parts[0]
            
            # Validate board structure
            ranks = position.split('/')
            if len(ranks) != 8:
                logger.warning("Invalid FEN: Wrong number of ranks")
                return False
            
            for rank in ranks:
                space_count = 0
                for char in rank:
                    if char.isdigit():
                        space_count += int(char)
                    else:
                        space_count += 1
                if space_count != 8:
                    logger.warning("Invalid FEN: Invalid rank length")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"FEN validation error: {e}")
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
        logger.info("Starting board state update...")
        logger.info(f"Before Moves Dict {self.moves_dict}")
        
        # Get new position information
        logger.info("5.1: Getting new occupied positions")
        new_pos = self.processor.get_occupied_positions()
        
        logger.info("5.2: Checking position differences")
        if chance :
            logger.info("H")
            results = self.processor.diff_checker(
                self.occupied_pos, 
                new_pos,
                moves_dict=self.moves_dict,
                chance=chance,
                fen_string=self.fen_string,
                play_state=self.play_state
            )
        else: 
            logger.info("R")
            results = {
                "src" : [self.src],
                "dst" : [self.dst]
            }
        
        logger.info("5.3: Updating occupied positions")
        logger.info(f" Occupied Pos :{new_pos}")
        self.occupied_pos = new_pos
        self.processor.save_json_data(self.occupied_pos,OCCUPIED_POS_PATH)
        

        # Update internal board state
        logger.info("5.4: Updating board state")
        self.moves_dict, self.fen_string, self.board = self.processor.update_fen_from_occupied_pos(
            results=results, 
            moves_dict=self.moves_dict, 
            board=self.board,
            chance=chance,
            fen_string=self.fen_string,
            play_state=self.play_state
        )
        
        # Get fresh legal moves for the new position
        logger.info("5.5: Refreshing legal moves dictionary")
        logger.info(f"FEN {self.fen_string}")
        self.moves_dict = self.processor.get_legal_moves(self.fen_string)
        
        # Update visual representation
        logger.info("5.6: Updating visual display")
        self.processor.board = self.board  # Sync processor's board with current state
        self.processor.generate_board_visuals()
        self.processor.display_board()
        logger.info(f"Final Moves Dict {self.moves_dict}")


    def main(self):
        """Main game loop with enhanced move validation and move type handling."""
        logger.info("Press Button to start each turn...")
        logger.info(f"Game State {self.game_state}")
        if self.game_state == ChessGameState.NORMAL:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((self.host, self.port))
                    while True:
                        data = s.recv(1024)
                        logger.info(data)
                        logger.info("ROBOT PLAYING .... Normal")
                        if data:
                            self.occupied_pos = self.processor.get_occupied_positions()
                            self.game_state = ChessGameState.RETRY
                            logger.info(f"Game state {self.game_state}")
                            break
                        elif data == b'':  # Handle empty data as connection termination
                            logger.error(" 🚨 Empty data received. Closing connection.")
                            # self.game_state = ChessGameState.RETRY
                            # s.close()
                            time.sleep(1)
                            error_handler(fen_string=self.fen_string, move="H")
                            logger.info("🚨Quiting🚨")
                            exit(0)
                            break
                        time.sleep(1)
                except socket.timeout:
                    logger.error("No data received, retrying...")
                    error_handler(fen_string=self.fen_string,move="H")
                except ConnectionRefusedError:
                    logger.error("Connection refused by the host.")
                    error_handler(fen_string=self.fen_string,move="H")
                    
        elif self.game_state == ChessGameState.RETRY:
            logger.warning("🚨 RETRYING 🚨")
            

        while True:
            # Display the board and read FEN string
            self.processor.generate_board_visuals()
            self.processor.display_board()

            self.moves_dict = self.processor.get_legal_moves(self.fen_string)
            logger.info(self.fen_string)
            if self.fen_string is None:
                logger.error("❌ ERROR : MAIN --> Error reading FEN string ❌")
                error_handler(fen_string=self.fen_string,state=self.play_state)
                logger.info("🚨Quiting🚨")
                exit(0)
                           
            # Check for game-ending state first
            if self.check_game_ending_state(self.fen_string):
                logger.info("\n🏁 GAME OVER 🏁")
                break
            
            # Check other game states
            if self.game_state in [ChessGameState.WHITE_CHECKMATE, 
                                ChessGameState.BLACK_CHECKMATE, 
                                ChessGameState.STALEMATE, 
                                ChessGameState.DRAW]:
                logger.info("\n🏁 GAME OVER 🏁")
                break

            # HUMAN TURN
            if self.human_move:
                logger.info(f"\n👤 Human Player's Turn , Play State : {PLAYSTATE_MAPPING[self.play_state]}👤")
                if self.play_state != PlayState.HUMAN_COMM_COMPLETE.value :
                
                    logger.info("Press SPACE when you've completed your move...")
                    self.play_state = PlayState.HUMAN_PLAYING.value

                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((self.host, self.port))
                            while True:
                                self.processor.generate_board_visuals()
                                self.processor.display_board()
                                # time.sleep(1)
                                logger.info("Waiting ... PRESS")
                                # data = s.recv(1024) 
                                # s.settimeout(5)  # Set timeout to 5 seconds
                                try:
                                    data = s.recv(1024)
                                    logger.info(f"Received: {data}")

                                    if data :
                                        self.play_state = PlayState.HUMAN_COMM_COMPLETE.value
                                        time.sleep(4)
                                        logger.info("Processing move....")

                                        # Update board state and validate move
                                        results = self.processor.diff_checker(
                                            self.occupied_pos, 
                                            self.processor.get_occupied_positions(),
                                            self.moves_dict,
                                            chance=1,
                                            fen_string=self.fen_string,
                                            play_state=self.play_state
                                        )
                                        
                                        # Only proceed if a valid move is detected
                                        if results['src'] and results['dst']:
                                            self.update_board_state(chance=1)
                                            self.robot_move = True
                                            self.human_move = False
                                            self.play_state = PlayState.HUMAN_PLAYING_DONE.value
                                            break
                                        else:
                                            logger.error("❌ ERROR : MAIN[HUMAN_MOVE] --> No valid move detected. ❌")
                                            error_handler(fen_string=self.fen_string,state=self.play_state)
                                            logger.info("🚨Quiting🚨")
                                            exit(0)
                                except socket.error as e:
                                    logger.error(f"❌ ERROR : MAIN[HUMAN_MOVE] --> Socket Connection failed :: {e}❌")
                                    error_handler(fen_string=self.fen_string,state=self.play_state)
                                    logger.info("🚨Quiting🚨")
                                    exit(0)
                                    break
                                except Exception as e:
                                    logger.error(f"❌ ERROR : MAIN[HUMAN_MOVE] --> Unexpected error during robot move: {e} ❌")
                                    error_handler(fen_string=self.fen_string,state=self.play_state)
                                    logger.info("🚨Quiting🚨")
                                    exit(0)
                else:
                    try:
                        time.sleep(2)
                        logger.warning("🚨 WARNING : MAIN[HUMAN_MOVE] --> Attempting to reupdate board state 🚨")

                        results = self.processor.diff_checker(
                                            self.occupied_pos, 
                                            self.processor.get_occupied_positions(),
                                            self.moves_dict,
                                            chance=1,
                                            fen_string=self.fen_string,
                                            play_state=self.play_state
                                        )
                        
                        # Only proceed if a valid move is detected
                        if results['src'] and results['dst']:
                            self.update_board_state(chance = 1)
                            self.robot_move = True
                            self.human_move = False
                            self.play_state = PlayState.HUMAN_PLAYING_DONE.value
                        else:
                            logger.error("❌ ERROR : MAIN[HUMAN_MOVE] --> Corners not detected ❌")
                            error_handler(fen_string=self.fen_string,state=self.play_state)
                            logger.info("🚨Quiting🚨")
                            exit(0)        
                    except Exception as e:
                            logger.error(f"❌ ERROR : MAIN[HUMAN_MOVE] --> Unexpected error during robot move: {e} ❌")
                            error_handler(fen_string=self.fen_string,state=self.play_state)
                            logger.info("🚨Quiting🚨")
                            exit(0)

            # ROBOT TURN
            elif self.robot_move:
                logger.info(f"\n🤖 Robot's Turn   Play State : {PLAYSTATE_MAPPING[self.play_state]} 🤖")
                if self.play_state != PlayState.ROBOT_COMM_COMPLETE.value :

                    self.play_state = PlayState.ROBOT_PLAYING.value
                    try:
                        # Get best move and execute it
                        self.src, self.dst, move_type = self.get_best_move(self.fen_string)

                        if self.src is None or self.dst is None:
                            logger.warning("🚨 WARNING: Game has Ended 🚨")
                            break

                        # Send move to robot
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.connect((self.host, self.port))

                            src_num = SQUARE_MAPPING[self.src]
                            dst_num = SQUARE_MAPPING[self.dst]
                            # logger.info move type in human-readable format
                            move_type_str = {
                                self.SIMPLE_MOVE: "SIMPLE",
                                self.ATTACK_MOVE: "ATTACK",
                                self.CASTLING_KS_MOVE: "CASTLING_KS",
                                self.CASTLING_QS_MOVE: "CASTLING_QS",
                            }[move_type]
                            
                            logger.info(f"Robot moving from {self.src} --> {self.dst} Move type: {move_type_str}")
                            move_data = f'{src_num},{dst_num},{move_type}'.encode()
                            s.sendall(move_data)

                            # Receive the response from the robot
                            response = s.recv(1024)
                            logger.info(f'✅ Robot move successfully executed: {repr(response)}')
                            self.play_state = PlayState.ROBOT_COMM_COMPLETE.value

                            time.sleep(2) # Wait for Camera stabilization before updating board state

                            # Update board state after robot's move
                            self.update_board_state(chance = 0)
                            self.robot_move = False
                            self.human_move = True
                            self.play_state = PlayState.ROBOT_PLAYING_DONE.value

                    except socket.error as err:
                        logger.error(f"❌ ERROR : MAIN[ROBOT_MOVE] --> Socket error: {err} ❌")
                        error_handler(fen_string=self.fen_string,state=self.play_state)
                        logger.info("🚨Quiting🚨")
                        exit(0)
                    except Exception as e:
                        logger.error(f"❌ ERROR : MAIN[ROBOT_MOVE] --> Unexpected error during robot move: {e} ❌")
                        error_handler(fen_string=self.fen_string,state=self.play_state)
                        logger.info("🚨Quiting🚨")
                        exit(0)
                else:
                    try:
                        time.sleep(2)
                        logger.warning("🚨 WARNING : MAIN[ROBOT_MOVE] --> Attempting to reupdate board state 🚨")
                        # Update board state after robot's move
                        self.update_board_state(chance = 0)
                        self.robot_move = False
                        self.human_move = True
                    except Exception as e:
                        logger.error(f"❌ ERROR : MAIN[ROBOT_MOVE] --> Unexpected error during robot move: {e} ❌")
                        error_handler(fen_string=self.fen_string,state=self.play_state)
                        logger.info("🚨Quiting🚨")
                        exit(0)
            time.sleep(0.1)



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
        self.board.set_castling_fen("-")
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
            logger.error(f"Error loading JSON from {file_path}: {e}")
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
        logger.info("Occupied json updated")
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
        logger.info("Getting legal moves for both sides...")
        
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
            
            # logger.info(f"Calculated moves for both sides: {all_moves}")
            return all_moves
            
        except Exception as e:
            logger.error(f"Error calculating legal moves: {e}")
            return {}

    def diff_checker(self, old_dict, new_dict, moves_dict, chance, fen_string , play_state):
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
        logger.info("In Diff checker")
        try:
            logger.info(f"Old Dict {old_dict}")
            logger.info(f"New Dict {new_dict}")
            logger.info(f"Moves Dict {moves_dict}")

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
            logger.info(f"src_squares {src_squares}")
            logger.info(f"Dst Squares {dst_squares}")
            validated_dst = []
            for dst in dst_squares:
                for moves in moves_dict.values():
                    # Check if any source square can legally move to this destination
                    if any(move[2:4] == dst and move[:2] in src_squares for move in moves):
                        validated_dst.append(dst)
                        break
            logger.info(f"Valid Dst Squares {validated_dst}")

            results = {
                "src": src_squares,
                "dst": list(set(validated_dst))  # Remove any duplicates
            }
            
            logger.info(f"Detected changes - Source: {results['src']}, Destination: {results['dst']}")
            return results
        except Exception as e:
            logger.error(f" ❌ ERROR : DIFF_CHECKER --> {e} ❌")
            error_handler(fen_string=fen_string,state=play_state)
            logger.info("🚨Quiting🚨")
            exit(0)

    # Function to convert file to 0-indexed integer
    def file_to_index(self,file):
        return ord(file) - ord('a')

    # Function to convert rank to 0-indexed integer
    def rank_to_index(self,rank):
        return int(rank) - 1

    def update_fen_from_occupied_pos(self, results, moves_dict, board, chance,fen_string , play_state):
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
            logger.info("Processing move results...")
            logger.info(results)

            # Get source and destination
            src_list = results.get("src", [None])
            dst_list = results.get("dst", [None])
            fen = board.fen()

            # Validate source and destination
            if not src_list or not dst_list:
                logger.error(" ❌ ERROR : UPDATE_FEN -->  Source or Destination square is missing. ❌")
                error_handler(fen_string=fen, state=play_state)
                logger.info("🚨 Quitting 🚨")
                exit(0)

            # Iterate through all possible source squares and destination squares and check for a valid move
            move = None
            piece_symbol = None
            matching_piece = None
            for src in src_list:
                for dst in dst_list:
                    potential_move = src + dst  # Combine source and destination into a move string
                    logger.info(f"Trying move: {potential_move}")

                    # Check if the move is valid for any piece in moves_dict
                    for piece, moves in moves_dict.items():
                        if potential_move in moves:
                            piece_symbol = piece[0]
                            matching_piece = piece
                            move = potential_move
                            break  # Stop once a valid move is found

                    if move:  # If a valid move is found, no need to check further
                        break  # Exit the inner loop once a valid move is found

                if move:  # If a valid move is found, no need to check further
                    break  # Exit the outer loop once a valid move is found

            if move:
                logger.info(f"Move determined: {move}")
            else:
                logger.error(f" ❌ ERROR : UPDATE_FEN --> No valid move found for {src_list} to {dst_list} ❌")
                error_handler(fen_string=fen, state=play_state)
                logger.info("🚨 Quitting 🚨")
                exit(0)

            logger.info(f"Moving PIECE: {piece_symbol} from {src} to {dst}")

            # Convert squares to board indices
            src_square = chess.parse_square(src)
            dst_square = chess.parse_square(dst)
            
            # Create and validate the move
            move_obj = chess.Move(src_square, dst_square)
            if move_obj not in board.legal_moves:
                logger.error(f"❌ ERROR : UPDATE_FEN -->  Illegal move attempted: {move} 🚨")
                error_handler(fen_string=fen_string,state=play_state)
                logger.info("🚨Quiting🚨")
                exit(0)
                # return moves_dict, board.fen(), board

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

            # logger.info(f"Updated Moves Dictionary: {updated_moves_dict}")
            logger.info(f"New FEN string: {board.fen()}")

            return updated_moves_dict, board.fen(), board
                
        except Exception as e:
            logger.error(f"❌ ERROR : UPDATE_FEN --> Error updating board state: {e} ❌")
            error_handler(fen_string=fen_string,state=play_state)
            logger.info("🚨Quiting🚨")
            exit(0)
            # if chance:
            #     error_handler(fen_string=board.fen(),move="H")
            #     logger.info("🚨Quiting🚨")
            #     exit(0)
            # else:
            #     error_handler(fen_string=board.fen(),move="R")
            #     logger.info("🚨Quiting🚨")
            #     exit(0)
            # return moves_dict, board.fen(), board
        
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
            logger.warning("🚨 WARNING : DISPLAY_BOARD --> Failed to load board image 🚨")

def error_handler(fen_string,state):
    logger.info(f"⚙️ Handling Error for {PLAYSTATE_MAPPING[state]}⚙️")
    time.sleep(3)
    try:
        if state in [PlayState.SETUP.value,
                     PlayState.ROBOT_PLAYING.value,
                     PlayState.ROBOT_COMM_COMPLETE.value,
                     PlayState.HUMAN_PLAYING_DONE] :
            move = "R"
        elif state in [PlayState.ROBOT_PLAYING_DONE.value,
                       PlayState.HUMAN_PLAYING.value,
                       PlayState.HUMAN_COMM_COMPLETE.value] :
            move = "H"

        chess_controller = ChessRobotController(fen_string=fen_string,move=move,ps=state)
        chess_controller.game_state == ChessGameState.RETRY
        chess_controller.main()
    except KeyboardInterrupt as e:
        logger.error(f"❌ GAME ENDED ❌")
        raise
    except Exception as e:
        logger.error(f"❌ Fatal error: {e} ❌")
        raise

def main():
    try:
        logger.info("\n🎮 WELCOME TO CHESS ROBOT GAME 🎮")
        chess_controller = ChessRobotController()
        chess_controller.main()
    except KeyboardInterrupt as e:
        logger.error(f"❌ GAME ENDED ❌")
        raise
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise

if __name__ == '__main__':
    main()
