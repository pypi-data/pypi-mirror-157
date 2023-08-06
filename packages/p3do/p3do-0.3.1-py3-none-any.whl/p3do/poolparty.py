#!/usr/bin/env python3

import os
from base64 import b64encode, b64decode

from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.padding import PKCS7

def encrypt(clear: str, password, salt, strength) -> str:
    kdf = PBKDF2HMAC(
        algorithm=SHA1(),
        # get bit need byte
        length=strength//8,
        # standard salt as used in `EncryptionService.java`
        salt=bytes(salt, "utf-8"),
        # always 1024, hardcoded in `EncryptionService.java`
        iterations=1024
    )
    # errors on purpose if encryption.password does not exist
    key = kdf.derive(bytes(password, "utf-8"))
    iv = os.urandom(16) # always 16, hardcoded in `EncryptionService.java`

    padder = PKCS7(16*8).padder() # know bytes need bits, AES blocksize must be == iv length
    ct_padded = padder.update(bytes(clear, "utf-8")) + padder.finalize()

    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ct = encryptor.update(ct_padded) + encryptor.finalize()

    return str(b64encode(iv+ct), "utf-8")


def decrypt(secret: str, password, salt, strength) -> str:
    kdf = PBKDF2HMAC(
        algorithm=SHA1(),
        # get bit need byte
        length=strength//8,
        # standard salt as used in `EncryptionService.java`
        salt=bytes(salt, "utf-8"),
        # always 1024, hardcoded in `EncryptionService.java`
        iterations=1024
    )
    # errors on purpose if encryption.password does not exist
    key = kdf.derive(bytes(password, "utf-8"))
    secret_bytes = b64decode(secret)
    iv, secret_bytes = (secret_bytes[:16], secret_bytes[16:])

    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    ct = decryptor.update(secret_bytes) + decryptor.finalize()

    unpadder = PKCS7(16*8).unpadder() # know bytes need bits, AES blocksize must be == iv length
    ct_unpadded = unpadder.update(ct) + unpadder.finalize()

    return ct_unpadded.decode("utf-8")
