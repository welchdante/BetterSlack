import socket 
import select 
import sys 
import os

import rsa_encrypt as rsa

class Client:
    def __init__(self, ip, port): 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.connect((ip, port))

		self.public_key = read_public_key()
		self.fernet_key = rsa.get_fernet_key()

		self.encrypted_public_key = gen_symmetric_key(public_key, fernet_key)
		self.server.send(fernet_key.encode()) # Send fernet immediately


    # listen for both user input to send out and data from server 
    def listen(self):

        while True: 
            input_streams = [sys.stdin, self.server] 
            read_sockets, write_socket, error_socket = select.select(input_streams,[],[]) 

            for socks in read_sockets: 
                if socks == self.server:
					message = rsa.decrypt_message(socks.recv(2048), fernet_key)
                    # message = socks.recv(2048) 
                    if message.decode() == "quit":
                        print("Shutting Down\n")
                        sys.exit()
                    print(message.decode())
                else:
                    message = sys.stdin.readline().replace('\n', '') 
                    encrypted_message = encrypt_message(message, fernet_key)
                    self.server.send(encrypted_message.encode()) 
        server.close() 

if len(sys.argv) != 3: 
    exit() 
ip = str(sys.argv[1]) 
port = int(sys.argv[2])

client = Client(ip, port)
client.listen()