import chess
import chess.engine

fen_string = "8/8/8/8/8/8/8/8 w - - 0 1"

board = chess.Board(fen_string)

if not board.is_valid():
    raise ValueError("Invalid board configuration from FEN string.")

# Initialize the Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci(".\\stockfish\\stockfish-windows-x86-64-avx2.exe")

# Get the best move with a time limit
result = engine.play(board, chess.engine.Limit(time=2.0))
