import select
import socket
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

# this will be in server 
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
    print(pub)
    #prob wanna write these to files or something idk
    return 0

# this will be in server
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

# this will be in server
def encrypt_message(message, recipient, symmetric_key_list):
    # Encrypt message to be sent to specified recipient
    fernet_key = symmetric_key_list.get(recipient)
    f = Fernet(fernet_key)
    encrypted_message = f.encrypt(message)
    return encrypted_message

#this will be in client
def decrypt_message(key, data, fernet_key):
    # Decrypt message sent from server 
    f = Fernet(fernet_key)
    message = f.decrypt(data)
    return message

#this will be in the client
def read_public_key()
    # Read public key from file and convert it to public_key type
    file = open("public_key.pem", "r")
    public_key_data = file.read()
    public_key = load_pem_public_key(public_key_data, backend=default_backend())
    return public_key

#this will be in the client
def gen_symmetric_key(public_key)
    # Generate symmetric key
    fernet_key = Fernet.generate_key()
    f = Fernet(fernet_key)

    # RSA encrypt the symmetric key
    encrypted_public_key = public_key.encrypt(
        fernet_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_public_key