import sys
import hashlib
import binascii


def base36encode(base10_number):
    """Takes a base10 int and returns a base36 string"""
    base36 = ''
    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    if 0 <= base10_number < len(alphabet):
        return alphabet[base10_number]
    while base10_number != 0:
        base10_number, i = divmod(base10_number, len(alphabet))
        base36 = alphabet[i] + base36
    return str(base36)


def read_input_arguments():
    """Simple input sanitization."""
    input_arguments = sys.argv
    # Check number of args
    number_of_args = len(input_arguments)
    if number_of_args != 2:
        print("Wrong number of arguments.")
        exit(1)
    # Check if input is a number
    if not input_arguments[1].isnumeric():  # isnumeric() returns true when >= 0
        print("Argument not a valid int.")
        exit(1)
    if int(input_arguments[1]) > 384:
        print("Argument too big. Max number of zero bits is 384.")
        exit(1)
    return int(input_arguments[1])


def find_hash_with_zeroes(number_of_zeroes):
    """This function tries to find a hash that is padded with zeroes with bruteforce.

    It works by incrementing and integer by one, turning it
    to base36 (which contains all the numbers and letters).
    This becomes the input to the hashing function.
    The zeroes are checked by turning the hash to a binary string and then
    simply comparing strings.
    """
    check_string = "0" * number_of_zeroes
    i = 0
    while True:
        data = base36encode(i)
        output = str(binascii.hexlify(hashlib.sha384(data.encode()).digest()))[2:-1]
        binary_string = "{:0384b}".format(int(bytes.fromhex(output).hex(), 16))  # to binary string parkour
        front_part = binary_string[:number_of_zeroes]
        i = i + 1
        if front_part == check_string:
            print(f"{data.encode('utf-8').hex()} {output}")
            break
    return


if __name__ == '__main__':
    """Main function"""
    num_of_zeroes = read_input_arguments()
    find_hash_with_zeroes(num_of_zeroes)
    exit(0)
