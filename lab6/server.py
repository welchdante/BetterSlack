import socket
import sys
import os
import signal
import threading
import errno

quit = {'quit', 'Quit', 'QUIT'}

def recv():
    message = ''
    try:
        while message not in quit:
            data = connection.recv(1024)
            if not data:
                sys.exit(0)
            message = data.decode()
            if message in quit:
                print('\nClient is leaving, you now have no friends. Bye!')
            else:
                sys.stdout.write('\nClient: ' + message + '\nYou: ')
    finally:
        try:
            connection.shutdown(socket.SHUT_RDWR)
            os.kill(os.getpid(), signal.SIGINT)
        except socket.error as error:
            if error.errno != 107:
                raise
            else:
                sys.stdout.write("Exiting")

port = int(input('Which port do you want to run the server on?'))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', port)

print('Starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

sock.listen(1)
print('Waiting for a client to connect...')
connection, client_address = sock.accept()

print('Got a connection from: ', client_address)

threading.Thread(target=recv).start()

try:
    message = ''
    while message not in quit:
        # Send data
        message = input('You: ')
        if message in quit:
            quit_message = 'quit'    
            connection.sendall(quit_message.encode('utf-8'))
        else: 
            connection.sendall(message.encode('utf-8'))

except KeyboardInterrupt:
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)

finally:
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except socket.error as error:
        if error.errno != 107:
            raise
        else:
            sys.stdout.write("Exiting")