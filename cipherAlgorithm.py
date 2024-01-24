from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import os


class CipherAlgorithm:

    def __init__(self):
        pass

    def encrypt_aes_gcm(self, plaintext):
        load_dotenv()
        key = os.getenv("SECRET_KEY").encode()
        iv = os.getenv("SECRET_IV").encode()

        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=backend)
        encryptor = cipher.encryptor()

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag

        return ciphertext, tag

    def decrypt_aes_gcm(self, ciphertext, tag):
        load_dotenv()
        key = os.getenv("SECRET_KEY").encode()
        iv = os.getenv("SECRET_IV").encode()

        backend = default_backend()
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=backend)
        decryptor = cipher.decryptor()

        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext


if __name__ == "__main__":
    cipher = CipherAlgorithm()
    tanje_info = 'Abrakadabra%34dsw093@#$&^%>:@#D'

    szyfr, tag = cipher.encrypt_aes_gcm(tanje_info.encode())
    print(szyfr, tag)

    deszyfr = cipher.decrypt_aes_gcm(szyfr, tag)
    print(deszyfr.decode())
