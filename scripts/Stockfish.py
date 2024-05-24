import chess
import chess.engine
import keyboard

def on_space_pressed(event):
    if event.name == 'space':
        print('Spacebar pressed')

keyboard.on_press(on_space_pressed)

# Keep the script running
keyboard.wait('esc') 

def get_best_move(fen_string):
    # Parse FEN string and set up the board
    board = chess.Board(fen_string)

    # Initialize Stockfish engine
    engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\\harsh\\Vipul\\ML\\Chess Detection ML\\AutomatedChessRobot\\scripts\\stockfish\\stockfish-windows-x86-64-avx2.exe")
    # Get best move
    result = engine.play(board, chess.engine.Limit(time=0.1))
    best_move = result.move

    # Close the engine
    engine.quit()

    return best_move, result

# Example usage
fen_string = "1nbkq3/ppp1bppp/3p1n2/1r2p2r/1R1PP2P/3N4/PPP1QPP1/1BN1KB1R w - - 0 1"
best_move, info = get_best_move(fen_string)

move = str(best_move)
source = move[:2]
destination = move[2:4]

print("Best move:", best_move)
print("Source square:", source, "Destination square:", destination)


