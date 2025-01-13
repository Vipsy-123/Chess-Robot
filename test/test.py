fen = "rnbqkbnr/ppp1pppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w - - 0 1"

# Split the FEN into parts
parts = fen.split()
chance = 1
# Check the condition and toggle the side-to-move
if chance:
    parts = board.fen().split()
    parts[1] = 'b' if parts[1] == 'w' else 'w'
    fen_string = " ".join(parts)

print(fen_string)
