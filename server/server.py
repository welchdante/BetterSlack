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
        self.list_of_clients = [] 

    # creates a new client to do client things
    def client_thread(self, conn, addr): 
        message = "Welcome to better than Slack!"
        conn.send(message.encode()) 
      
        while True: 
            try: 
                message = conn.recv(2048) 
                if message: 
                    print("<" + addr[0] + "> " + message.decode())
                    message_to_send = "<" + addr[0] + "> " + message.decode() 
                    self.send_message_to_all(message_to_send, conn) 
                else:
                    self.remove(conn) 
      
            except: 
                continue

    # sends message to all clients connected that are not the connection
    def send_message_to_all(self, message, connection): 
        for client in self.list_of_clients: 
            if client != connection: 
                try: 
                    client.send(message.encode()) 
                except: 
                    client.close()
                    self.remove(client) 

    # remove a connection from the list
    def remove(self, connection): 
        if connection in self.list_of_clients: 
            self.list_of_clients.remove(connection) 

    # listen for new clients
    def serve(self): 
        while True:
            conn, addr = self.server.accept() 
            self.list_of_clients.append(conn) 
            print(addr[0] + " connected")
            start_new_thread(self.client_thread,(conn,addr))  
        
        conn.close() 
        self.server.close() 


if len(sys.argv) != 3:
    exit() 

IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server = Server(IP_address, Port)
server.serve()