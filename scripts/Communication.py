
import chess
import chess.engine
import keyboard
import time
import socket
import json

robot_move = True
human_move = False
occupied_pos_path = '../saved_files/occupied_positions.json'

# Create a mapping dictionary for chessboard squares to numerical values
square_mapping = {
    'a1': 1, 'a2': 2, 'a3': 3, 'a4': 4, 'a5': 5, 'a6': 6, 'a7': 7, 'a8': 8,
    'b1': 9, 'b2': 10, 'b3': 11, 'b4': 12, 'b5': 13, 'b6': 14, 'b7': 15, 'b8': 16,
    'c1': 17, 'c2': 18, 'c3': 19, 'c4': 20, 'c5': 21, 'c6': 22, 'c7': 23, 'c8': 24,
    'd1': 25, 'd2': 26, 'd3': 27, 'd4': 28, 'd5': 29, 'd6': 30, 'd7': 31, 'd8': 32,
    'e1': 33, 'e2': 34, 'e3': 35, 'e4': 36, 'e5': 37, 'e6': 38, 'e7': 39, 'e8': 40,
    'f1': 41, 'f2': 42, 'f3': 43, 'f4': 44, 'f5': 45, 'f6': 46, 'f7': 47, 'f8': 48,
    'g1': 49, 'g2': 50, 'g3': 51, 'g4': 52, 'g5': 53, 'g6': 54, 'g7': 55, 'g8': 56,
    'h1': 57, 'h2': 58, 'h3': 59, 'h4': 60, 'h5': 61, 'h6': 62, 'h7': 63, 'h8': 64
}


def read_string_from_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def get_pressed_key():
    key = keyboard.read_key()
    return key

# Function to load JSON data from file with error handling
def load_json_data(file_path):
    try:
        with open(file_path) as json_file:
            return json.load(json_file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading JSON from {file_path}: {e}")
        return {}

occupied_pos = load_json_data(occupied_pos_path)

def play(fen_string):
    global robot_move, human_move,occupied_pos # Declare variables as global
 
    if robot_move:
        print("Robot's Chance")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))  # Connect the socket
            src, dst, attk = get_best_move(fen_string)
            if occupied_pos.get(dst, 0) == 1:  # Check if the destination is occupied
                attk = 1
            else: 
                attk = 0
                
            # Map the source and destination to numerical values
            src_num = square_mapping[src]
            dst_num = square_mapping[dst]

            s.sendall(f'{src_num},{dst_num},{attk}'.encode())  # Send the points as numbers
            data = s.recv(1024)
            print('Robot move Successfully executed', repr(data))
            # print("Socket Communication Successful")
            robot_move = False
            human_move = True
            time.sleep(2)
        except socket.error as err:
            print("ERROR in play():: ", err)
            # Handle the error gracefully, maybe retry or log the error

    if human_move:
        print("Human Player's Chance")
        while True:
            # After Human move is Completed he/she will press Space for the Robot to move
            if keyboard.is_pressed('space'):
                robot_move = True
                human_move = False
                break

 

def get_best_move(fen_string):
    # Parse FEN string and set up the board
    board = chess.Board(fen_string)
    try:
        # Initialize Stockfish engine
        engine = chess.engine.SimpleEngine.popen_uci(".\stockfish\stockfish-windows-x86-64-avx2.exe")
        # Get best move
        result = engine.play(board, chess.engine.Limit(time=0.1))
        best_move = result.move
        move = str(best_move)
        source = move[:2]
        destination = move[2:4]
        attack = False # Bool that will help robot to take attack decision
        # Close the engine
        engine.quit()
        print("Source square:", source, "Destination square:", destination)
        return source, destination, attack
    except Exception as e:
        print("ERROR in get_move():: ",e)
        print("PRESS SPACE TO CONTINUE")
        raise e

# Example usage
# fen_string = "1nbkq3/ppp1bppp/3p1n2/1r2p2r/1R1PP2P/3N4/PPP1QPP1/1BN1KB1R w - - 0 1"


def main(args=None):
    # keyboard.on_press(on_space_pressed)
    
    robot_move = True
    human_move = False
    occupied_pos = load_json_data(occupied_pos_path)
    print("WELCOME TO CHESS ROBOT GAME")
    print("PRESS SPACE TO CONTINUE")
    while(True):
        # Obtain the FEN string from fen.txt file
        filename = "../saved_files/fen.txt"
        try:
            fen_string = read_string_from_file(filename)
        except Exception:
             print("Can't Read fEN String")
        # print("String read from file:", fen_string)

        if(keyboard.is_pressed('space')):
            print("Key pressed !!")
            play(fen_string)
        # Keep the script running
        # keyboard.wait('esc') 


if __name__ == '__main__':
    try:
        host = '192.168.0.20'
        port = 10002
        s = socket.socket (socket.AF_INET,socket.SOCK_STREAM)
        s.connect(host,port)
    except Exception as e :
        print("Got ", e)
    main()
