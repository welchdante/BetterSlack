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
            data = sock.recv(1024)
            if not data:
                sys.exit(0)
            message = data.decode()
            if message in quit:
                print('\nServer is leaving, you now have no friends. Bye!')
            else:
                sys.stdout.write('\nServer: ' + message + '\nYou: ')

    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
            os.kill(os.getpid(), signal.SIGINT)
        except socket.error as error:
            if error.errno != 107:
                raise
            else:
                print("Exiting")

port = int(input('Which port do you want to connect the client to?'))
ip_address = input('Which IP address do you want to connect the client to?')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (ip_address, port)

sys.stdout.write('connecting to {} port {}\n'.format(*server_address))
sock.connect(server_address)

threading.Thread(target=recv).start()

try:
    message = ''
    while message not in quit:
        message = input('You: ')

        if message in quit:
            quit_message = 'quit'    
            sock.sendall(quit_message.encode('utf-8'))
        else: 
            sock.sendall(message.encode('utf-8'))

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
            print("Exiting")