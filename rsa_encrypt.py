import select
import socket
import sys
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.serialization import load_pem_public_key



'''
DONE Randomly generate symmetric key    
Encrypt symmetric key with RSA pub key
Decrypt symmetric key with RSA private key
Encrypting all chat messages with symmetric key
Decrypting all chat messages with symmetric key
Correct use of initialization vector
'''

# Server - Used...
def generate_keys():
    # Generate keys
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    priv = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    priv.splitlines()[0]

    public_key = private_key.public_key()
    pub = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    pub.splitlines()[0]
    print(priv)
    print()
    file = open("public_key.pem", "wb")
    print(pub)
    file.write(pub)
    file.close()
    return priv, pub

# Server - Used...
def decrypt_symmetric_key(private_key, data):
    # Decrypt message with private key
    message = private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return message

# Server - Used...
def encrypt_message(message, recipient, symmetric_key_list, fernet_key = None):
    if fernet_key is None:
        # Encrypt message to be sent to specified recipient
        fernet_key = symmetric_key_list.get(recipient)
        f = Fernet(fernet_key)
    else:
        f = Fernet(fernet_key)
    encrypted_message = f.encrypt(message)
    return encrypted_message

# Client
def decrypt_message(data, fernet_key):
    # Decrypt message sent from server 
    f = Fernet(fernet_key)
    message = f.decrypt(data)
    return message

# Client
def read_public_key():
    # Read public key from file and convert it to public_key type
    file = open("public_key.pem", "rb")
    public_key_data = file.read()
    file.close()
    public_key = load_pem_public_key(public_key_data, backend=default_backend())
    return public_key

# Client
def gen_symmetric_key(public_key, fernet_key):
    # Generate symmetric key
    f = Fernet(fernet_key)
    salt = os.urandom(16)

    # RSA encrypt the symmetric key
    encrypted_public_key = public_key.encrypt(
        fernet_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        )
    )
    return encrypted_public_key

# Client
def get_fernet_key():
    return Fernet.generate_key()


