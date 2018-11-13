import socket 
import select 
import sys 
from _thread import *

import rsa_encrypt as rsa

'''
decrypted_message = rsa.decrypt_symmetric_key(self.priv, message)
encrypted_message = encrypt_message(message, recipient, symmetric_key_list)
'''

class Server:
    def __init__(self, ip, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server.bind((ip, port))
        self.server.listen(100)   
        self.list_of_clients = {} 
        self.symmetric_key_list = {}

        self.priv, self.pub = rsa.generate_keys()

    # creates a new client to do client things
    def client_thread(self, conn, addr, username): 
        message = "Welcome to Better than Slack! For a list of commands, enter -help."
        
        # TODO Possibly encrypt this message?
        conn.send(message.encode()) 

        while True: 
            try: 
                message = rsa.decrypt_symmetric_key(self.priv, conn.recv(2048)) 
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
                        conn.send(rsa.encrypt_message(admin_name, username, self.symmetric_key_list).encode())

                        admin_bytes = rsa.decrypt_symmetric_key(self.priv, conn.recv(2048))
                        admin_name = admin_bytes.decode()

                        # Get admin password
                        admin_pass = "Admin Password:"
                        conn.send(rsa.encrypt_message(admin_pass, username, self.symmetric_key_list).encode())

                        admin_bytes = rsa.decrypt_symmetric_key(self.priv, conn.recv(2048))
                        admin_pass = admin_bytes.decode() 

                        if admin_name == "admin" and admin_pass == "admin":
                            admin_commands = '''Admin commands:\n\t-list: lists the current users\n\t-rm <user to remove>: remove a user\n'''
                            conn.send(rsa.encrypt_message(admin_commands, username, self.symmetric_key_list).encode()) 

                            admin_action = "Which action would you like to take?"
                            conn.send(rsa.encrypt_message(admin_action, username, self.symmetric_key_list).encode())

                            admin_bytes = rsa.decrypt_symmetric_key(self.priv, conn.recv(2048))
                            admin_action = admin_bytes.decode()

                            if admin_action[:3] == "-rm":
                                user = admin_action.split()[1]

                                if user in self.list_of_clients:
                                    client = self.list_of_clients[user]
                                    message = 'quit'
                                    conn.send(rsa.encrypt_message(message, username, self.symmetric_key_list).encode())

                                    self.remove(conn, user)
                                    print('User notified and removed.')
                                else:
                                    print("User not found.\n")
                            else:
                                print("Command doesn't require admin rights.\nPlease try again.\n")
                        else:
                            admin_commands = "Permission Denied\n"
                            conn.send(rsa.encrypt_message(admin_commands, username, self.symmetric_key_list).encode())
 
                    # quit the program
                    elif decoded_message[:5] == '-quit':
                        exit_command = "quit"
                        conn.send(rsa.encrypt_message(exit_command, username, self.symmetric_key_list).encode())
                        print("-quit recieved\nShutting down:", username)
                        self.remove(conn, username)
 
                    # user wants help 
                    elif decoded_message[:5] == '-help':
                        help_commands = '''Help commands:\n\t-list: lists the current users\n\t-pm <user to send to> <message to send>: send a private message\n\t-admin <admin command>: perform administrative commands\n\t-quit: kills the program and removes the connected user\n'''
                        conn.send(rsa.encrypt_message(help_commands, username, self.symmetric_key_list).encode())
  
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
            
            client.send(rsa.encrypt_message(message, username, symmetric_key_list).encode())

        else:
            error_message = "That user cannot be found, please enter a user in the chat room."
            connection.send(rsa.encrypt_message(error_message, username, self.symmetric_key_list).encode())

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
        connection.send(rsa.encrypt_message(connected_users_message, username, self.symmetric_key_list).encode())

    # sends message to all clients connected that are not the connection
    def send_message_to_all(self, message, connection): 
        for username in self.list_of_clients: 
            client = self.list_of_clients[username]
            if client != connection: 
                try:
                    client.send(rsa.encrypt_message(message, username, self.symmetric_key_list).encode())
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
            encrypted_public_key = conn.recv(2048)
            username_prompt = "What is your username?"
            conn.send(username_prompt.encode())

            valid_username = False
            while not valid_username:
                username_bytes = rsa.decrypt_symmetric_key(self.priv, conn.recv(2048))
                username = username_bytes.decode() # TODO May need to move decode into the decrypt function
                if username not in self.list_of_clients:
                    valid_username = True
                    self.symmetric_key_list[username] = encrypted_public_key # New
                    self.list_of_clients[username] = conn
                else:
                    already_exists = "User already exists, please enter a new username." 
                    conn.send(rsa.encrypt_message(already_exists, username, self.symmetric_key_list).encode())

            connected_message = username + " connected"
            print(connected_message)
            conn.send(rsa.encrypt_message(connected_message, username, self.symmetric_key_list).encode())
            start_new_thread(self.client_thread,(conn, addr, username))  
         
        conn.close() 
        self.server.close() 


if len(sys.argv) != 3:
    exit() 

IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 
server = Server(IP_address, Port)
server.serve()