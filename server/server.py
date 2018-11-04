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
                    decoded_message = message.decode()                   
                    print(username + ": " + decoded_message)
                    # command to get all other active users
                    if decoded_message[:5] == '-list':
                        connected_users = self.get_connected_users(conn)
                        self.send_connected_users(connected_users, conn)

                    # command to send to a specific client
                    elif decoded_message[:3] == '-pm':
                        print("send a private message")

                    # administrative commands
                    elif decoded_message[:6] == '-admin':
                        print("Do admin stuff")

                    elif decoded_message[:5] == '-help':
                        print("help commands")

                    # no command was entered
                    else:
                        message_to_send =  username + ": " + message.decode().replace('\n', '')
                        self.send_message_to_all(message_to_send, conn) 
                else:
                    self.remove(conn) 
      
            except: 
                continue

    def get_connected_users(self, connection):
        connected_users = []
        for username in self.list_of_clients:
            client = self.list_of_clients[username]
            if client != connection:
                connected_users.append(username)
        return connected_users

    def send_connected_users(self, connected_users, connection):
        connected_users_message = ', '.join(connected_users)
        connected_users_message = 'Connected users: ' + connected_users_message
        connection.send(connected_users_message.encode())

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