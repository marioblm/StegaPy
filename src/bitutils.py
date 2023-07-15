def string2bits(input_string=''):
    """
        Converts a string to a list of binary strings, each representing one character.

        :param input_string: The input string.

        :return: A list of binary strings, each of length 8.
    """
    binary_strings = []
    for x in input_string:
        utf8_code = ord(x)
        if utf8_code.bit_length() > 8:
            raise ValueError("Only 8 bit characters are supported")
        binary_string = bin(utf8_code)[2:]
        padded_binary_string = binary_string.zfill(8)
        binary_strings.append(padded_binary_string)
    return binary_strings


def bits2string(input_bits=None):
    """
        Converts a binary string to its unicode representation.

        :param input_bits: A binary string, of length 8*n.

        :return: The output string of length n.
    """
    output_string = ""
    for i in range(0, len(input_bits), 8):
        byte = input_bits[i:i + 8]
        # convert byte to unicode character
        output_string += chr(int(byte, 2))
    return output_string
