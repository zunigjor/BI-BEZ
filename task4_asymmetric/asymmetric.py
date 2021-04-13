# author: Jorge Zuniga (zunigjor)
import sys
import os
from functools import partial
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives import hashes


def open_files(input_file_name, output_file_name):
    file_in = open(input_file_name, "rb")
    if file_in.closed:
        print(f"Could not open {input_file_name}")
        raise FileNotFoundError("Could not open output file")
    file_out = open(output_file_name, "wb")
    if file_out.closed:
        print(f"Could not open {output_file_name}")
        file_in.close()
        raise FileNotFoundError("Could not open output file")
    return file_in, file_out


def encrypt(public_RSA_key_file_name, input_file_name, output_file_name, secret_key, initialization_vector):
    """Encryption using a PUBLIC key to encrypt a key to encrypt the input file
    pubkey.pem:param
    message.txt:param
    K and IV are random
    E_sym (f, k, IV) -> message_enc     # https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
    E_asym (K, pubkey) -> K_enc         # https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#encryption
    encrypted_message.txt = K_enc + IV + message_enc
    """
    # ---------------- read RSA public key ---------------- #
    with open(public_RSA_key_file_name, "rb") as public_RSA_key_file:
        try:
            public_key = serialization.load_pem_public_key(public_RSA_key_file.read())
        except ValueError:
            print(f"ERROR: {public_RSA_key_file_name} does not contain a public RSA key")
            public_RSA_key_file.close()
            exit(1)
    # ---------------- open required files ---------------- #
    try:
        file_in, file_out = open_files(input_file_name, output_file_name)
    except FileNotFoundError:
        public_RSA_key_file.close()
        exit(1)
    # ---------------- encrypt secret_key using public key ---------------- #
    encrypted_secret_key = public_key.encrypt(secret_key,
                                              asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                                                                algorithm=hashes.SHA256(),
                                                                label=None))
    # ---------------- write enc_secret_key ---------------- #
    print(f"key_enc: {encrypted_secret_key}")
    print(f"size: {len(encrypted_secret_key)}")
    file_out.write(encrypted_secret_key)
    # ---------------- write initialization_vector ---------------- #
    file_out.write(initialization_vector)
    # ---------------- encrypt the message using secret_key ---------------- #
    # ---------------- AES 256 + CBC ---------------- #
    cipher = Cipher(algorithms.AES(secret_key), modes.CBC(initialization_vector))
    encryptor = cipher.encryptor()
    for chunk in iter(partial(file_in.read, 1024), b''):
        if len(chunk) != 1024:  # end of file has been reached, has to be padded and encrypted
            break
        file_out.write(encryptor.update(chunk))
    padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
    chunk = padder.update(chunk) + padder.finalize()  # pad the last chunk
    file_out.write(encryptor.update(chunk) + encryptor.finalize())
    return


def decrypt(private_RSA_key_file_name, input_file_name, output_file_name):
    """Decrypt uses a PRIVATE key to decrypt the encrypted message
    The encrypted file contains an encrypted secret key and initialization vector as a header.
    # ---------------- DECRYPTION  pseudocode ---------------- #
    encrypted_message.txt = K_enc + IV + enc_message.txt
    D_asym (K_enc, privkey.pem)    -> K # https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa/#decryption
    D_sym (message_enc.txt, K, IV) -> message # https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption
    """
    # ---------------- read RSA private key ---------------- #
    with open(private_RSA_key_file_name, "rb") as private_RSA_key_file:
        try:
            private_key = serialization.load_pem_private_key(private_RSA_key_file.read(), password=None)
        except ValueError:
            print(f"ERROR: {private_RSA_key_file_name} does not contain a private RSA key")
            private_RSA_key_file.close()
            exit(1)
    # ---------------- calculate number of bytes to read encrypted key ---------------- #
    key_bytes_size = int(private_key.key_size / 8)
    print(f"bsize: {key_bytes_size}")
    # ---------------- open required files ---------------- #
    try:
        file_in, file_out = open_files(input_file_name, output_file_name)
    except FileNotFoundError:
        private_RSA_key_file.close()
        exit(1)
    # ---------------- read header ---------------- #
    # ---------------- read encrypted key ---------------- #
    encrypted_secret_key = file_in.read(key_bytes_size)
    # ---------------- decrypt key using private RSA key ---------------- #
    secret_key = private_key.decrypt(encrypted_secret_key,
                                     asym_padding.OAEP(mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                                                       algorithm=hashes.SHA256(),
                                                       label=None))
    # ---------------- read 128byte initialization_vector ---------------- #
    initialization_vector = file_in.read(16)
    # ---------------- decrypt the rest of the message using secret_key and initialization_vector ---------------- #
    # ---------------- AES 256 + CBC ---------------- #
    cipher = Cipher(algorithms.AES(secret_key), modes.CBC(initialization_vector))
    decryptor = cipher.decryptor()
    for chunk in iter(partial(file_in.read, 1024), b''):
        if len(chunk) != 1024:  # end of file has been reached, has to be decrypted and unpadded
            break
        file_out.write(decryptor.update(chunk))
    decrypted_chunk_with_padding = decryptor.update(chunk) + decryptor.finalize()
    unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_chunk = unpadder.update(decrypted_chunk_with_padding) + unpadder.finalize()
    file_out.write(unpadded_chunk)
    return


def validate_input(encrypt_decrypt, key_file_name, input_file_name):
    valid_encrypt_decrypt = ["-e", "-d"]
    if encrypt_decrypt not in valid_encrypt_decrypt:
        print(f"ERROR: Invalid encryption/decryption param.")
        exit(1)
    if not os.path.exists(key_file_name):
        print(f"ERROR: File {key_file_name} not found.")
        exit(1)
    if not os.path.exists(input_file_name):
        print(f"ERROR: File {input_file_name} not found.")
        exit(1)
    return


def main():
    # ---------------- check args ---------------- #
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} <-e or -d> <key file name> <input file name> <output file name>")
        exit(1)
    # ---------------- read args ---------------- #
    encrypt_decrypt = sys.argv[1]
    key_file_name = sys.argv[2]
    input_file_name = sys.argv[3]
    output_file_name = sys.argv[4]
    secret_key = os.urandom(32)  # 256 bytes
    initialization_vector = os.urandom(16)  # 128 bytes
    # ---------------- validate input ---------------- #
    validate_input(encrypt_decrypt, key_file_name, input_file_name)
    # ---------------- encrypt / decrypt ---------------- #
    if encrypt_decrypt == "-e":
        encrypt(key_file_name, input_file_name, output_file_name, secret_key, initialization_vector)
    elif encrypt_decrypt == "-d":
        decrypt(key_file_name, input_file_name, output_file_name)
    # ---------------- print output file name and end ---------------- #
    print(output_file_name)
    exit(0)


if __name__ == '__main__':
    main()
