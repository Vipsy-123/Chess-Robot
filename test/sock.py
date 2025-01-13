import socket 

def main():
    host = '192.168.0.20'
    port = 10002 
    try : 
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
        s.connect((host,port)) 
        # Convert the string to bytes and then send its
        s.sendall(b'1')
        data = s.recv(1024) 
        print('Received:', data.decode())  # Decode received bytes to string
        print("Socket success") 
    except socket.error as err: 
        print("Socket error")    

if __name__ == "__main__":
    main()
