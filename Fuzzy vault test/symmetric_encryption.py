import os
from Crypto.Cipher import AES
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def encrypt_vault_512_bit_key():
    
    with open("vault/vault.txt", "rb") as f:
        file_content = f.read()
    
    # 512-bit key
    key = os.urandom(64)

    # Salt should be a random value that is unique for each key derivation
    salt = os.urandom(16)

    # Number of iterations should be high enough to make the key derivation slow
    iterations = 100000

    # Derive a 256-bit key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256,
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )

    key = kdf.derive(key)

    # Generate a 16-byte initialization vector (IV)
    iv = os.urandom(16)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    # The string to be encrypted
    plaintext = file_content

    # Padding the plaintext to a multiple of 16 bytes
    padding = 16 - (len(plaintext) % 16)
    plaintext += bytes([padding]) * padding

    # Encrypting the plaintext
    ciphertext = cipher.encrypt(plaintext)
    
    # Encoding the ciphertext to base64
    ciphertextBase = base64.b64encode(ciphertext)
    
    with open("vault/encryptedVault.txt", 'w') as file:
        file.write(ciphertextBase.decode())
    
    return ciphertextBase,key,iv

def encrypt_vault_256_bit_key():
    
    with open("vault/vault.txt", "rb") as f:
        file_content = f.read()
    
    # 256-bit key
    key = os.urandom(32)

    # Generate a 16-byte initialization vector (IV)
    iv = os.urandom(16)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    # The string to be encrypted
    plaintext = file_content

    # Padding the plaintext to a multiple of 16 bytes
    padding = 16 - (len(plaintext) % 16)
    plaintext += bytes([padding]) * padding

    # Encrypting the plaintext
    ciphertext = cipher.encrypt(plaintext)
    
    # Encoding the ciphertext to base64
    ciphertextBase = base64.b64encode(ciphertext)
    
    with open("vault/encryptedVault.txt", 'w') as file:
        file.write(ciphertextBase.decode())
    
    return ciphertextBase,key,iv

def decrypt_vault(ciphertextBase,key,iv):
    
    # Decoding the ciphertext from base64
    ciphertext = base64.b64decode(ciphertextBase)

    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypting the ciphertext
    plaintext = cipher.decrypt(ciphertext)

    # Removing the padding
    padding = plaintext[-1]
    plaintext = plaintext[:-padding]
    
    with open("vault/decryptedVault.txt", 'w') as file:
        file.write(plaintext.decode())   
    
if __name__ == '__main__':
    
    # ciphertextBase,key,iv = encrypt_vault_512_bit_key()
    ciphertextBase,key,iv = encrypt_vault_256_bit_key()
    decrypt_vault(ciphertextBase,key,iv)
    
    with open("vault/vault.txt", "rb") as f:
        file_content1 = f.read()
        
    with open("vault/encryptedVault.txt", "rb") as f:
        file_content2 = f.read()
        
    print(file_content1==file_content2)
 