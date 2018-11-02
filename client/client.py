import socket 
import select 
import sys 

class Client:
    def __init__(self, ip, port): 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.connect((ip, port))

    # listen for both user input to send out and data from server 
    def listen(self):

        while True: 
            input_streams = [sys.stdin, self.server] 
            read_sockets, write_socket, error_socket = select.select(input_streams,[],[]) 

            for socks in read_sockets: 
                if socks == self.server:
                    message = socks.recv(2048) 
                    print(message.decode())
                else:
                    message = sys.stdin.readline().replace('\n', '') 
                    self.server.send(message.encode()) 
        server.close() 

if len(sys.argv) != 3: 
    exit() 
ip = str(sys.argv[1]) 
port = int(sys.argv[2])

client = Client(ip, port)
client.listen()