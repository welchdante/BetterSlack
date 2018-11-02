import socket 
import select 
import sys 
from _thread import *
  
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

if len(sys.argv) != 3:
    exit() 

IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 

server.bind((IP_address, Port)) 
server.listen(100)   
list_of_clients = [] 
  
def client_thread(conn, addr): 
    message = "Welcome to better than Slack!"
    conn.send(message.encode()) 
  
    while True: 
            try: 
                message = conn.recv(2048) 
                if message: 
                    print("<" + addr[0] + "> " + message.decode())
                    message_to_send = "<" + addr[0] + "> " + message.decode() 
                    send_message_to_all(message_to_send, conn) 
                else:
                    remove(conn) 
  
            except: 
                continue
  
def send_message_to_all(message, connection): 
    for clients in list_of_clients: 
        if clients!=connection or 1: 
            try: 
                clients.send(message.encode()) 
            except: 
                clients.close()
                remove(clients) 

def remove(connection): 
    if connection in list_of_clients: 
        list_of_clients.remove(connection) 
  
while True:
    conn, addr = server.accept() 
    list_of_clients.append(conn) 
    print(addr[0] + " connected")
    start_new_thread(client_thread,(conn,addr))     
  
conn.close() 
server.close() 
