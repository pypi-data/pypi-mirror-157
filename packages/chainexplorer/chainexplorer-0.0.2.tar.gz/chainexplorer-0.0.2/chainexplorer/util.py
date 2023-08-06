"""Block Explorer Util Module Documentation.

The Util module offers convenience functions to work motr efficiently with Block Explorer data.'


"""

import re
import os
from itertools import product
from typing import Tuple


def write_binary_to_file(data: bytes, file_name: str) -> None:
    """Function to write binary data to file.

    Args:
        data: Binary data to be written to file.
        file_name: Output file name. For example: image.jpg

    """

    assert isinstance(data, bytes), "Input data is not of type bytes"

    with open(file_name, "wb") as file:
        file.write(data)


def write_to_txt(data: str, file_name: str) -> None:
    """Function to write data to .txt file.

    Args:
        data: Data to be written to .txt file.
        file_name: Output file name. For example: raw_data.txt
        mode: mode for writing to the text file. Follows the Python syntax.

    """

    assert isinstance(data, str), f'input must be of type str not: {type(data)}'

    if not file_name.endswith('.txt'):
        file_name = add_extension(file_name, 'txt')

    with open(file_name, "a+", encoding="utf-8") as file:

        # Check if something is already inside the file. If so start a new line.
        file.seek(0)
        if len(file.read(1)) == 1:
            file.write('\n')
        
        file.write(data)


def read_from_txt(file_name: str) -> list:
    """Function to read data from .txt file.

    Args:
        file_name: Data to be written to .txt file.

    Returns:
        Content of the .txt file

    """

    with open(file_name, "r", encoding="utf-8") as file:
        lines = []
        for next_line in file:
            lines.append(next_line.strip())

    return lines


def find_markers(data: str) -> dict:
    """Function to identify the start and the end of various file formats within a string sequence.
    If multiple potential starts and ends are found all will be returned

    Args:
        data: String that contains the data. The string has to contain the data as hex values.

    Returns:
        The index of all potential beginnings of a data file and the index of the potential ends within the
        input string. The markers are returned for each potential file type.

    """

    formats = {
        'png': ['89504e470d', '44ae426082'],
        'jpg': ['ffd8', 'ffd9'],
        'gif': ['4749463839614E015300C4', '2100003B00'],
        'zip': ['504B030414', '504B050600'],
        'mp3': ['494433', '494433']
    }

    markers = {}
    for item in formats.items():

        header_marker = item[1][0]
        footer_marker = item[1][1]

        try:
            header_index = [sof.start() for sof in re.finditer(header_marker, data)]
            footer_index = [eof.start() + len(footer_marker) for eof in re.finditer(footer_marker, data)]

            if footer_index and header_index and footer_index[0] - header_index[-1] == len(header_marker):
                footer_index = [len(data)]

        except IndexError:
            header_index = []
            footer_index = []

        markers[item[0]] = [header_index, footer_index]

    return markers


def match_markers(markers: list) -> Tuple[list, list]:
    """Function to validate and match file markers retrieved with find_file_markers.
    For example, Start of Image (SOI) or End of Image (EOI) markers can randomly occur in image
    as well as non-image data. The typical expectation is to find as many SOI markers as EOI markers.

    This function takes the SOI markers and looks for matches in the EOI markers based on two criteria:
    1. The EOI marker must come after the SOI marker
    2. The total length of the SOI to EOI interval must be even, otherwise decoding to binary is not possible

    Both measures improve the quality of the markers but are no guaranty that the markers are no false positive.

    Args:
        markers: dictionary

    Returns:
        SOI and EOI file markers in two separate lists

    """

    # Create all possible file start/end combinations
    file_markers = list(product(markers[0], markers[1]))

    # Remove the invalid file start/end combinations
    file_markers = list(filter(lambda x: (x[0] < x[1]), file_markers))
    file_markers = list(filter(lambda x: ((x[0] + x[1]) % 2 == 0), file_markers))

    start_of_file = [x[0] for x in file_markers]
    end_of_file = [x[1] for x in file_markers]

    return start_of_file, end_of_file


def create_folder(directory: str) -> None:
    """Function to create a new directory or a directory with sub-directories.py

    Args:
        directory: String that contains the directory structure to be created

    """
    if not os.path.isdir(directory):
        os.makedirs(directory)


def is_transaction(transaction: str) -> bool:
    """Function to check if an input is Bitcoin transaction hash ot not.

    Args:
        transaction: String to be tested if it is a transaction hash

    Returns:
        Result if input string represents a valid transaction hash or not
    """

    return len(transaction) == 64 and isinstance(transaction, str) and is_sha256(transaction)


def add_extension(file_name: str, file_extension: str) -> str:
    """Function to add an extension to a file name

     Args:
         file_name: String with the target file name lacking the extension (e.g. .txt)
         file_extension: String with the extension to be added.

    Returns:
        File name with correct extension.

     """

    return f"{file_name.strip('.')}.{file_extension}"


def is_base58(test_string: str) -> bool:
    """Function to check if a string is following the base58 convention or not.

    Args:
        test_string: String that will be tested if it is base58.

    Returns:
        True if all characters in the string are base58 and False otherwise.

    """
    base58_characters = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    return all(x in base58_characters for x in test_string)


def is_sha256(test_string: str) -> bool:
    """Function to check if a string is a SHA256 hash.

    Args:
        test_string: String that will be tested if it is SHA256

    Returns:
        True if all characters in the string are SHA256 and False otherwise.

    """
    sha256_characters = '0123456789ABCDEFabcdef'

    return all(x in sha256_characters for x in test_string)


def byte_to_string(byte_data: [bytes, list]) -> list:
    """Convert byte encoded data to string

    Args:
        byte_data: Data of interest either as a single byte object or as a list of byte objects.

    Returns:
        Input byte data as string as a list.

    """

    if isinstance(byte_data, bytes):
        byte_data = [byte_data]

    str_data = []
    for data in byte_data:

        converted = data.decode('utf8', errors="ignore")
        str_data.append(converted)

    return str_data
