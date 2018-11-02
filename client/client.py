
# Python program to implement client side of chat room. 
import socket 
import select 
import sys 
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
if len(sys.argv) != 3: 
    exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server.connect((IP_address, Port)) 
  
while True: 
    input_streams = [sys.stdin, server] 
    read_sockets,write_socket, error_socket = select.select(input_streams,[],[]) 
  
    for socks in read_sockets: 
        if socks == server: 
            message = socks.recv(2048) 
            print(message.decode()) 
        else: 
            message = sys.stdin.readline() 
            server.send(message.encode()) 
            sys.stdout.write("<You>") 
            sys.stdout.write(message) 
            sys.stdout.flush() 
server.close() 
