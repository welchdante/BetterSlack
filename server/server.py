import socket 
import select 
import sys 
from _thread import *

class Server:
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server.bind((ip, port))
        self.server.listen(100)   
        self.list_of_clients = {} 

    # creates a new client to do client things
    def client_thread(self, conn, addr, username): 
        message = "Welcome to Better than Slack!"
        conn.send(message.encode()) 
        
        while True: 
            try: 
                message = conn.recv(2048) 
                if message:
                    print(username + ": " + message.decode())
                    message_to_send =  username + ": " + message.decode().replace('\n', '')
                    self.send_message_to_all(message_to_send, conn) 
                else:
                    self.remove(conn) 
      
            except: 
                continue

    # sends message to all clients connected that are not the connection
    def send_message_to_all(self, message, connection): 
        for username in self.list_of_clients: 
            client = self.list_of_clients[username]
            if client != connection: 
                try:
                    client.send(message.encode()) 
                except: 
                    client.close()
                    self.remove(client, username) 

    # remove a connection from the list
    def remove(self, connection, username): 
        if username in self.list_of_clients: 
            del self.list_of_clients[username]

    # listen for new clients
    def serve(self): 
        while True:
            conn, addr = self.server.accept()
            username_prompt = "What is your username?"
            conn.send(username_prompt.encode())
            valid_username = False
            while not valid_username:
                username_bytes = conn.recv(2048)
                username = username_bytes.decode()

                if username not in self.list_of_clients:
                    valid_username = True
                    self.list_of_clients[username] = conn
                else:
                    already_exists = "User already exists, please enter a new username." 
                    conn.send(already_exists.encode())
            
            connected_message = username + " connected"
            print(connected_message)
            conn.send(connected_message.encode())
            start_new_thread(self.client_thread,(conn, addr, username))  
         
        conn.close() 
        self.server.close() 


if len(sys.argv) != 3:
    exit() 

IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server = Server(IP_address, Port)
server.serve()