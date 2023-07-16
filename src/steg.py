import secrets
import math
from os import path
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import cv2
import numpy as np

from .bitutils import *
from .header import *

FILL_WITH_NOISE = False


def get_optimal_setup(message_size, medium):
    """
    Calculate the optimal settings needed to encode the message.

    :param message_size: The size of the message in bytes.
    :param medium: The medium to hide the message in.

    :return: A list containing the optimal setup [bits_per_pixel, use_all_channels].
    
    :raises OverflowError: If the message does not fit into the medium.
    """
    if message_size < medium.shape[0] * medium.shape[1]:
        return [1, False]
    if message_size < np.prod(medium.shape):
        return [1, True]
    needed_bits = math.ceil(message_size / np.prod(medium.shape))
    if needed_bits < HeaderUtils().max_bits_per_pixel:
        return [needed_bits, True]
    raise OverflowError("Message does not fit into medium!")


def ensure_correct_setup(setup, msg_size, medium):
    """
    Ensures that the settings are suitable for hiding the message in the given medium.

    :param setup: The setup for hiding the message, as a list containing [bits_per_pixel, use_all_channels].
    :param msg_size: The size of the message in bytes.
    :param medium: The medium to hide the message in.

    :return: The corrected setup if necessary, or the original setup if it is already valid.
    """
    msg_size += HeaderUtils().header_length
    if setup is None:
        return get_optimal_setup(msg_size, medium)
    if msg_size > medium.shape[0] * medium.shape[1] * setup[0] * (3 if setup[1] else 1):
        print("Invalid setup, choosing setup automatically...")
        return get_optimal_setup(msg_size, medium)
    return setup


def reshape_array(arr, num_columns=3):
    """
    Reshape a 1-dimensional array into a 2-dimensional array with a specified number of columns.
    :param arr: The 1-dimensional array to be reshaped.
    :param num_columns: The desired number of columns in the reshaped array.

    :return: The reshaped array.
    """
    num_rows = (len(arr) + num_columns - 1) // num_columns
    num_padding = num_rows * num_columns - len(arr)
    
    padded_array = np.pad(arr, (0, num_padding), mode='constant')
    arr = padded_array.reshape(num_rows, num_columns)

    return arr


def encode(medium_filename, message_filename, hidden_filename, key=None, setup=None):
    """
    Encode a message into an image file using LSB Steganography.

    :param medium_filename: The filename of the medium to hide the message in.
    :param message_filename: The filename of the message file to be hidden.
    :param hidden_filename: The filename of the resulting steganographic image file.
    :param key: (Optional) The encryption key to encrypt the message.
    :param setup: (Optional) The setup for hiding the message, as a list containing [bits_per_pixel, use_all_channels].

    :raises FileNotFoundError: If the medium file is not found.
    :raises ValueError: If the message file is not found.
    :raises OverflowError: If there is insufficient space in the medium to hide the message.
    """
    image = cv2.imread(medium_filename)
    if image is None:
        raise FileNotFoundError("Medium not found")
    with open(message_filename, "rb") as f:
        msg = f.read()
    if msg is None:
        raise ValueError("Message not found")
    if key is not None:
        # encrypt data
        nonce = secrets.token_bytes(12)
        msg = nonce + AESGCM(key).encrypt(nonce, msg, b"")
    if hidden_filename is None:
        hidden_filename = "hidden"

    msg = ''.join(format(byte, '08b') for byte in msg)
    
    filetype = path.splitext(message_filename)[1][1:]
    nr_bits, use_all_channels = ensure_correct_setup(setup, len(msg), image)
    header_bits = HeaderUtils().encode_header(len(msg), filetype, nr_bits, use_all_channels, key is not None)

    header_mask = 1
    mask = ~((1 << nr_bits) - 1)

    flat_image = image.reshape(-1, image.shape[-1])
    header_array = [int(bdigit) for bdigit in header_bits]
    msg_array = [int(msg[i:i+nr_bits], 2) for i in range(0, len(msg), nr_bits)]

    header_array = reshape_array(header_array)
    flat_image[:len(header_array)] = (flat_image[:len(header_array)] & header_mask) + header_array 

    if use_all_channels:
        msg_array = reshape_array(msg_array)
    else:
        if FILL_WITH_NOISE:
            noise_shape = (len(msg_array), 1)
            noise_array = np.ravel(np.random.randint(2, size=noise_shape))
            noise_array2 = np.ravel(np.random.randint(2, size=noise_shape))
            msg_array = np.stack((msg_array,noise_array,noise_array2), axis=-1)
        else:
            msg_array = np.stack((msg_array,msg_array,msg_array), axis=-1)

    msg_slice = slice(len(header_array), len(header_array) + len(msg_array))
    flat_image[msg_slice] = (flat_image[msg_slice] & mask) + msg_array

    image = flat_image.reshape(image.shape)
    if not hidden_filename.endswith(".png"):
        hidden_filename += ".png"
    cv2.imwrite(hidden_filename, image)
    print("Message was hidden in {}".format(hidden_filename))


def write_bytes_to_file(bytes, file_extension, file_name):
    """
    Write bytes to a file with the specified file extension and name.

    :param bytes: The bytes to be written to the file.
    :param file_extension: The file extension.
    :param file_name: The name of the file.
    """
    file_name = "{}.{}".format(file_name or "message", file_extension)
    with open(file_name, "wb") as f:
        f.write(bytes)
    print("Message written to {}".format(file_name))


def extract_bits(image, bits=1, all_channels=True):
    """
    Extract the specified number of bits from an image.

    :param image: The image to extract bits from.
    :param bits: The number of bits to extract per pixel.
    :param all_channels: A boolean indicating whether to extract bits from all color channels.

    :return: A list of extracted bits as binary strings.
    """
    mask = (1 << bits) - 1
    if not all_channels:
        image = image[:, :, ::3]
    result = image & mask
    result = [bin(x)[2:].zfill(bits) for x in np.ravel(result)]
    return result


def fetch_data_from_file(filename):
    """
    Fetch data hidden within an image file using LSB Substitution.

    :param filename: The filename of the image file containing the hidden data.

    :return: A tuple (extracted data as bytes, the filetype, whether it was encrypted or not).
    """
    image = cv2.imread(filename)
    image_array = np.array(image)

    bits_list = extract_bits(image_array)
    binary_string = ''.join([str(x) for x in bits_list])

    header_data = binary_string[:HeaderUtils().header_length]
    length, filetype, bits, all_channels, enc = HeaderUtils().decode_header(header_data)
    settings_differ_from_header = bits > 1 or not all_channels

    if settings_differ_from_header:
        bits_list = extract_bits(image_array, bits, all_channels)
        binary_string = ''.join([str(x) for x in bits_list])

    data_start = len(header_data)*bits
    if not all_channels:
        data_start = math.ceil(data_start / 9) * 3
    else:
        data_start += 2 * bits

    cut_data = binary_string[data_start:data_start+length]
    bytes_data = bytes([int(cut_data[i:i+8], 2) for i in range(0, len(cut_data), 8)])
    return bytes_data, filetype, enc


def decode(filename="hidden.png", key=None, output_name=None):
    """
    Decodes a hidden message from an image file.

    :param filename: The name of the image file containing the hidden message.
    :param key: The encryption key used to decrypt the message.
    :param output_name: The name of the output file (without extension).

    :raises: ValueError if the key is missing and the message is encrypted.
    :raises: InvalidTag if the decryption fails.
    """
    values, filetype, enc = fetch_data_from_file(filename)
    if enc:
        if key is None:
            raise ValueError("Decryption key is missing")
        else:
            values = AESGCM(key).decrypt(values[:12], values[12:], b"")
    write_bytes_to_file(values, filetype, output_name)