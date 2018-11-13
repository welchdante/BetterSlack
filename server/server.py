import socket 
import select 
import sys 
from _thread import *
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

class Server:
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server.bind((ip, port))
        self.server.listen(100)   
        self.list_of_clients = {} 
        with open("../RSApriv.pem",mode="rb") as file:
            self.raw_priv = file.read()
        self.private_key = serialization.load_pem_private_key(
            self.raw_priv,
            password=None,
            backend=default_backend()
        )

    # creates a new client to do client things
    def client_thread(self, conn, addr, username): 
        message = "Welcome to Better than Slack! For a list of commands, enter -help."
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
                        self.send_private_message(decoded_message, conn)

                    # administrative commands
                    elif decoded_message[:6] == '-admin':
                        
                        # Get admin username
                        admin_name = "Admin Username:"
                        conn.send(admin_name.encode()) 
                        admin_bytes = conn.recv(2048)
                        admin_name = admin_bytes.decode()

                        # Get admin password
                        admin_pass = "Admin Password:"
                        conn.send(admin_pass.encode())
                        admin_bytes = conn.recv(2048)
                        admin_pass = admin_bytes.decode() 


                        if admin_name == "admin" and admin_pass == "admin":
                            admin_commands = '''Admin commands:\n\t-list: lists the current users\n\t-rm <user to remove>: remove a user\n'''
                            conn.send(admin_commands.encode()) 

                            admin_action = "Which action would you like to take?"
                            conn.send(admin_action.encode())

                            admin_bytes = conn.recv(2048)
                            admin_action = admin_bytes.decode()

                            if admin_action[:3] == "-rm":
                                user = admin_action.split()[1]

                                if user in self.list_of_clients:
                                    client = self.list_of_clients[user]
                                    message = 'quit'
                                    client.send(message.encode())
                                    self.remove(conn, user)
                                    print('User notified and removed.')
                                else:
                                    print("User not found.\n")
                            else:
                                print("Command doesn't require admin rights.\nPlease try again.\n")
                        else:
                            admin_commands = "Permission Denied\n"
                            conn.send(admin_commands.encode())                    

                    # quit the program
                    elif decoded_message[:5] == '-quit':
                        exit_command = "quit"
                        conn.send(exit_command.encode())
                        print("-quit recieved\nShutting down:", username)
                        self.remove(conn, username)

                    # user wants help 
                    elif decoded_message[:5] == '-help':
                        help_commands = '''Help commands:\n\t-list: lists the current users\n\t-pm <user to send to> <message to send>: send a private message\n\t-admin <admin command>: perform administrative commands\n\t-quit: kills the program and removes the connected user\n'''
                        conn.send(help_commands.encode())                        

                    else: # no command was entered
                        message_to_send =  username + ": " + message.decode().replace('\n', '')
                        self.send_message_to_all(message_to_send, conn) 
                else:
                    self.remove(conn, username)
      
            except: 
                continue

    def send_private_message(self, message, connection):
        split_message = message.split(' ')
        user = split_message[1]
        if user in self.list_of_clients:
            client = self.list_of_clients[user]
            message = ' '.join(split_message[2:])
            client.send(message.encode())
        else:
            error_message = "That user cannot be found, please enter a user in the chat room."
            connection.send(error_message.encode())

    def get_connected_users(self, connection):
        connected_users = []
        for username in self.list_of_clients:
            client = self.list_of_clients[username]
            if client == connection: 
                connected_users.append(username + " (you)")
            else:
                connected_users.append(username)
        return connected_users

    def send_connected_users(self, connected_users, connection):
        connected_users_message = ', '.join(connected_users)
        connected_users_message = 'Connected users: ' + connected_users_message
        print(connected_users_message)
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
            
            raw_in = conn.recv(2048)
            self.sym_key = self.decrypt_string(raw_in)
            fernet = Fernet(self.sym_key.decode())
            print(self.sym_key)

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

    def decrypt_string(self, data):
        decrypted_string = self.private_key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
        ))
        return decrypted_string

if len(sys.argv) != 3:
    exit() 

IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server = Server(IP_address, Port)
server.serve()