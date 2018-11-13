import socket 
import select 
import sys 
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

class Client:
    def __init__(self, ip, port): 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.connect((ip, port))
        with open("../RSApub.pem",mode="rb") as file:
            self.pub_key = load_pem_public_key(file.read(), backend=default_backend())
        self.sym_key = Fernet.generate_key()
        self.fernet = Fernet(self.sym_key)

    # listen for both user input to send out and data from server 
    def listen(self):

        self.encrypted_symmetric_key = self.pub_key.encrypt(
            self.sym_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA1()),
                algorithm=hashes.SHA1(),
                label=None
            )
        )
        self.server.send(self.encrypted_symmetric_key)
        print(self.sym_key)

        counter = 0
        while True: 
            input_streams = [sys.stdin, self.server] 
            read_sockets, write_socket, error_socket = select.select(input_streams,[],[]) 

            for socks in read_sockets: 
                if socks == self.server:
                    message = socks.recv(2048) 
                    try:
                        message = self.fernet.decrypt(message) # Breaks here... :(
                    except Exception as e:
                        pass
                    if message.decode() == "quit":
                        print("Shutting Down\n")
                        sys.exit()
                    print(message.decode())
                else:
                    message = sys.stdin.readline().replace('\n', '') 
                    val = self.fernet.encrypt(message.encode())
                    self.server.send(val) 
        server.close() 

if len(sys.argv) != 3: 
    exit() 
ip = str(sys.argv[1]) 
port = int(sys.argv[2])

client = Client(ip, port)
client.listen()