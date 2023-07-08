import os
from Crypto.Cipher import AES
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

# AES Encryption
# https://medium.com/swlh/an-introduction-to-the-advanced-encryption-standard-aes-d7b72cc8de97#:~:text=An%20initialization%20vector%20(or%20IV,is%20an%20added%20security%20layer.
# The difference in five modes in the AES encryption algorithm
# https://www.highgo.ca/2019/08/08/the-difference-in-five-modes-in-the-aes-encryption-algorithm/

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

def concatanate2BytesObject(object_1, object_2):
    # Use a known delimiter
    delimiter = b'|'

    # Concatenate the two keys
    concatenated_object = object_1 + delimiter + object_2
    
    return concatenated_object

def deConcatanate2UnknownLenthBytesObject(concatenated_object):
    delimiter = b'|'
    
    # Deconcatenate the key
    object_1_end = concatenated_object.index(delimiter)
    object_1 = concatenated_object[:object_1_end]
    object_2 = concatenated_object[object_1_end + len(delimiter):]

    return object_1,object_2

def convertBytesObjectToInteger(byte_object):
    # Convert binary data to integer
    integer_value = int.from_bytes(byte_object, byteorder='big')
    
    return integer_value

def convertIntegerToBytesObject(integer_value):
    # Convert integer back to binary data
    byte_object = integer_value.to_bytes(len(integer_value), byteorder='big')
    
    return byte_object
    
if __name__ == '__main__':
    
    # ciphertextBase,key,iv = encrypt_vault_512_bit_key()
    # ciphertextBase,key,iv = encrypt_vault_256_bit_key()
    # print(key)
    # print(iv)
    
    # concatenated_object = concatanate2BytesObject(key,iv)
    # print(concatenated_object)
    # object_1,object_2 = deConcatanate2UnknownLenthBytesObject(concatenated_object)
    # print(key==object_1)
    # print(iv==object_2)
    
    # decrypt_vault(ciphertextBase,key,iv)
    
    # with open("vault/vault.txt", "rb") as f:
    #     file_content1 = f.read()
        
    # with open("vault/encryptedVault.txt", "rb") as f:
    #     file_content2 = f.read()
        
    # print(file_content1==file_content2)
    
    byte_object = b'\xe2\x13h\xf4t2d\xa7`.Y\xfff\xa7l\t\xd7F\xf7;&\x7f\x03k6\xa2\xe5q\xc7\x05*\xd0|H\xe2\x05\x10\xa9\x9bsX\x85\xc1\xc5\xb7\xd5\xfbk\xa5'
    integer_value = convertBytesObjectToInteger(byte_object)
    
    new_byte_object = convertIntegerToBytesObject(integer_value)
    
    print(byte_object == new_byte_object)
    
    
 with open("vault/vault.txt", "rb") as f:
            file_content = f.read()