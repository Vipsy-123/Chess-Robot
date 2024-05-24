
import chess
import chess.engine
import keyboard
import time
import socket

robot_move = True
human_move = False

def read_string_from_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def get_pressed_key():
    key = keyboard.read_key()
    return key


def play(fen_string):
    global robot_move, human_move  # Declare variables as global
 
    if robot_move:
        print("Robot's Chance")
        try:
            src , dst , attk = get_best_move(fen_string)
            s.sendall (b'1,5,0') # Need to send point like P1,P2,P3
            data = s.recv (1024)
            print('Received ' , repr(data))
            print("Socket Communication Successful")
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
        engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\\harsh\\Vipul\\ML\\Chess Detection ML\\AutomatedChessRobot\\scripts\\stockfish\\stockfish-windows-x86-64-avx2.exe")
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
