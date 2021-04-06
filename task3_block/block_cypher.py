# author: Jorge Zuniga (zunigjor)
import sys
import os
from functools import partial
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

# Key and initialization vector hardcoded to be able to encrypt and decrypt images across multiple runs of the program.
KEY = b'7\x83W\x9eM\xcd\xca\xde\xd7\x14\xe1\x16g8\xec\x15kM\xf1\xc9\x87\xff\xe9\x12|\xe9\xdf\xd0\xd6\\NT'
IV = b'\xa1\x97\t\xf3I\xb5\xd6\xa5]\xfc\x8f\xba\x05\xe6\x95\xee'
# If required key and IV can be generated like this:
# KEY = os.urandom(32)
# IV = os.urandom(16)
# Using them like this changes them every time the program runs and therefore the encrypted images cannot be decrypted
# anymore.
# print(f"KEY: {KEY}")
# print(f"IV: {IV}")


def copy_tga_file_header(file_in, file_in_size, file_out):
    # ---------------- read 18 header bytes  ---------------- #
    header = file_in.read(18)
    id_field_chars = header[0:][:1]         # Number of Characters in Identification Field. range: 0-255, 0 = no IdFld.
    color_map_length = header[5:][:2]       # Integer ( lo-hi ) count of color map entries.
    color_map_entry_size = header[7:][:1]   # Number of bits in each color map entry. 16/24/32
    # ---------------- read the ID bytes  ---------------- #
    id_field_chars_int = int.from_bytes(id_field_chars, byteorder="little")
    header += file_in.read(id_field_chars_int)
    # ---------------- read the color map bytes  ---------------- #
    color_map_length_int = int.from_bytes(color_map_length, byteorder="little")  # Int count of color map entries.
    color_map_entry_size_int = int.from_bytes(color_map_entry_size, byteorder="little")  # 16/24/32
    color_map_int = color_map_length_int * int(color_map_entry_size_int / 8)
    header += file_in.read(color_map_int)
    # ---------------- check file_in validity  ---------------- #
    if (id_field_chars_int + 18 > file_in_size or color_map_int + 18 > file_in_size
            or id_field_chars_int + color_map_int + 18 > file_in_size):
        print("Bad input file.")
        file_in.close()
        file_out.close()
        exit(1)
    # ---------------- write the header into the output file  ---------------- #
    file_out.write(header)
    return


def encrypt(operation_mode, file_in, file_out):
    if operation_mode == "ecb":
        cipher = Cipher(algorithms.AES(KEY), modes.ECB())
    elif operation_mode == "cbc":
        cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV))
    encryptor = cipher.encryptor()
    for chunk in iter(partial(file_in.read, 1024), b''):
        if len(chunk) != 1024:  # end of file has been reached, has to be padded and encrypted
            break
        file_out.write(encryptor.update(chunk))
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    chunk = padder.update(chunk) + padder.finalize()  # pad the last chunk
    file_out.write(encryptor.update(chunk) + encryptor.finalize())
    return


def decrypt(operation_mode, file_in, file_out):
    if operation_mode == "ecb":
        cipher = Cipher(algorithms.AES(KEY), modes.ECB())
    elif operation_mode == "cbc":
        cipher = Cipher(algorithms.AES(KEY), modes.CBC(IV))
    decryptor = cipher.decryptor()
    for chunk in iter(partial(file_in.read, 1024), b''):
        if len(chunk) != 1024:  # end of file has been reached, has to be decrypted and unpadded
            break
        file_out.write(decryptor.update(chunk))
    decrypted_chunk_with_padding = decryptor.update(chunk) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    unpadded_chunk = unpadder.update(decrypted_chunk_with_padding) + unpadder.finalize()
    file_out.write(unpadded_chunk)
    return 0


def open_files(file_in_name, file_out_name):
    file_in = open(file_in_name, "rb")
    if file_in.closed:
        print(f"Could not open {file_in_name}")
        file_in.close()
        exit(1)
    file_out = open(file_out_name, "wb")
    if file_out.closed:
        print(f"Could not open {file_out_name}")
        file_in.close()
        file_out.close()
        exit(1)
    return file_in, file_out


def get_file_out_name(file_name, encrypt_decrypt, operation_mode):
    file_out_name = file_name[:-4]
    suffix = file_name[-4:]
    if encrypt_decrypt == "-e":
        if operation_mode == "ecb":
            file_out_name += "_ecb" + suffix
        elif operation_mode == "cbc":
            file_out_name += "_cbc" + suffix
    elif encrypt_decrypt == "-d":
        file_out_name += "_dec" + suffix
    return file_out_name


def validate_input(encrypt_decrypt, operation_mode, file_in_name):
    valid_encrypt_decrypt = ["-e", "-d"]
    valid_operation_mode = ["ecb", "cbc"]
    if len(sys.argv) != 4 or encrypt_decrypt not in valid_encrypt_decrypt or operation_mode not in valid_operation_mode:
        print(f"Usage: {sys.argv[0]} <-e or -d> <ecb or cbc> <file_in_name.tga>")
        exit(1)
    if file_in_name[-4:] != '.tga' and file_in_name[-4:] != '.TGA':
        print(f"Wrong file format. {file_in_name} suffix not \".tga\" or \".TGA\"")
        exit(1)
    if not os.path.exists(file_in_name):
        print(f"File {file_in_name} not found.")
        exit(1)
    file_size = os.stat(file_in_name).st_size
    if file_size == 0:
        print(f"{file_in_name} is empty")
        exit(1)
    if file_size < 18:
        print(f"{file_in_name} is missing header")
        exit(1)
    return file_size


def main():
    """main"""
    # ---------------- read args  ---------------- #
    encrypt_decrypt = sys.argv[1]
    operation_mode = sys.argv[2]
    file_in_name = sys.argv[3]
    # ---------------- validate input ---------------- #
    file_in_size = validate_input(encrypt_decrypt, operation_mode, file_in_name)
    file_out_name = get_file_out_name(file_in_name, encrypt_decrypt, operation_mode)
    # ---------------- open required files ---------------- #
    file_in, file_out = open_files(file_in_name, file_out_name)
    # ---------------- write the header, image ID and color map ---------------- #
    copy_tga_file_header(file_in, file_in_size, file_out)
    # ---------------- encrypt / decrypt ---------------- #
    if encrypt_decrypt == "-e":
        encrypt(operation_mode, file_in, file_out)
    elif encrypt_decrypt == "-d":
        decrypt(operation_mode, file_in, file_out)
    # ---------------- close files ---------------- #
    file_in.close()
    file_out.close()
    print(file_out_name)
    exit(0)


if __name__ == '__main__':
    main()
