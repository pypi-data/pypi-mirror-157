# -*- coding: utf-8 -*-
"""Block Explorer Module Documentation.

Block Explorer offers functions to retrieve information about blocks on the Bitcoin Blockchain via 'blockchain.info'


"""

from typing import Tuple
from typing import Union
import codecs
import time
import warnings
import requests
from chainexplorer import util


def __show_info(raw_block: dict) -> None:
    """Function to show the block information in the console.

    Args:
        raw_block: Block information as dictionary retrieved by either 'get_by_block' or 'get_by_hash'

    """

    for key in raw_block.keys():
        if key != 'tx':
            print(key + ': ' + str(raw_block[key]))


def get_latest_block() -> dict:
    """Function to retrieve all data from the latest block of the Bitcoin blockchain.

    Returns:
        dict: raw block data from the latest block

    """

    url = 'https://blockchain.info/latestblock'

    return requests.get(url).json()


def get_by_block(block_number: int) -> dict:
    """Function to retrieve all data from a specified block of the Bitcoin blockchain by providing the block number.

    Args:
        block_number: block number of interest

    Returns:
        dict: raw block data

    """

    url = 'https://blockchain.info/block-height/'

    return requests.get(url + str(block_number) + "?format=json").json()['blocks'][0]


def get_by_hash(block_hash: str) -> dict:
    """Function to retrieve all data from a specified block of the Bitcoin blockchain by providing the block hash.

    Args:
        block_hash: block hash of interest

    Returns:
        dict: raw block data

    """

    url = 'https://blockchain.info/rawblock/'

    return requests.get(url + block_hash).json()


def get_transaction(tx_hash: str) -> dict:
    """Function to retrieve all data from a specified transaction of
    the Bitcoin blockchain by providing the transaction hash.

    Args:
        tx_hash: transaction hash of interest

    Returns:
        dict: raw transaction data. iF the input is not a valid transaction hash an empty list is returned.

    """

    url = 'https://blockchain.info/rawtx/'

    raw_data = []
    if util.is_transaction(tx_hash):
        raw_data = requests.get(url + tx_hash).json()
    else:
        warnings.warn('Input is not a valid transaction hash.')

    return raw_data


def get_multi_address(address: str) -> dict:
    """Function to retrieve all information about a  or multiple addresses

    Args:
        address: address of interest address

    Returns:
        dict: raw data on the address history

    """

    url = 'https://blockchain.info/multiaddr?active='

    return requests.get(url + address).json()


def collect_messages(raw_block: dict) -> Tuple[list, list]:
    """Function to collect all input and output messages into two lists.

    Args:
        raw_block: Block information as dictionary retrieved by either 'get_by_block' or 'get_by_hash'

    Returns:
        tuple: with the input and output messages as lists

    """

    input_msg = []
    output_msg = []
    for i in raw_block['tx']:
        for output in i['out']:
            output_msg.append(output['script'])

        for inputs in i['inputs']:
            input_msg.append(inputs['script'])

    return input_msg, output_msg


def show_block_info(raw_block: dict) -> None:
    """Function to print block information in the console.

    Args:
        raw_block: Block information as dictionary retrieved by either 'get_by_block' or 'get_by_hash'

    """

    __show_info(raw_block)


def show_transactions(raw_block: dict) -> None:
    """Function to print the transaction data from a raw block in the console.

    Args:
         raw_block: Block information as dictionary retrieved by either 'get_by_block' or 'get_by_hash'

    """

    for count, tx in enumerate(raw_block['tx']):

        print(f'\n\nData of transaction: {count}\n')

        for key in tx.keys():
            print(key + ': ' + str(tx[key]))


def show_transaction_info(raw_tx: dict) -> None:
    """Function to collect general information about a transaction and print it in the console.

    Args:
        raw_tx: Transaction information as dictionary retrieved by 'get_transaction'.

    """

    total_input_value = 0
    for input_value in raw_tx['inputs']:
        total_input_value += input_value['prev_out']['value']

    total_output_value = 0
    for output_value in raw_tx['out']:
        total_output_value += output_value['value']

    assert total_output_value == total_input_value - raw_tx['fee']

    number_confirmations = get_latest_block()['height'] - raw_tx['block_index']

    tx_info = {
        'hash': raw_tx['hash'],
        'time': raw_tx['time'],
        'size': raw_tx['size'],
        'weight': raw_tx['weight'],
        'block_index': raw_tx['block_index'],
        'number_confirmations': number_confirmations,
        'total_input_value': total_input_value,
        'total_output_value': total_output_value,
        'fee': raw_tx['fee']
    }

    __show_info(tx_info)


def decode_hex_message(msg: Union[str, list]) -> list:
    """Function to decode hexadecimal messages to ASCII code.

    Args:
        msg: hexadecimal message either as a string or a list of strings.

    Returns:
        list: decoded hexadecimal input messages

    Examples:
        >>> decode_hex_message('5361746f736869')
        ['Satoshi']

    """

    if isinstance(msg, str):
        msg = [msg]

    decoded_msg = []
    for message in msg:

        decoded = codecs.decode(message, 'hex')
        decoded_msg.append(decoded)

    return decoded_msg


def collect_uploaded_data(raw_tx: dict) -> str:
    """Function to format and collect all outputs from a transaction that contains
    data uploaded via the Satoshi upload tool.

    Args:
        raw_tx: Transaction information as dictionary retrieved by 'get_transaction'.

    Returns:
        str: formatted outputs

    """

    data = ''
    for output in raw_tx['out']:
        cur = 4
        data = data + output['script'][cur:cur + 130]
        cur += 132
        data = data + output['script'][cur:cur + 130]
        cur += 132
        data = data + output['script'][cur:cur + 130]

    return data


def download_data(tx_hash: str, file_name: str) -> None:
    """Function to easily download data from the Bitcoin Blockchain.

    Args:
        tx_hash: transaction hash of interest that contains the data
        file_name: filename to which the data will be written

    """

    raw_tx = get_transaction(tx_hash)
    data = collect_uploaded_data(raw_tx)
    decoded_data = decode_hex_message(data[16:-112])[0]

    util.write_binary_to_file(decoded_data, file_name)


def collect_out_scripts(raw_tx: dict, max_value: float = float('inf'), spent: bool = False) -> list:
    """Function to collect all the scripts from a transaction. By default, all transactions will be collected
    independent of their value. Also, all spent transactions will be skipped in the collection process.

    Args:
        raw_tx: transaction hash of interest that contains the data
        max_value: Allows to set a threshold for the value of each transaction that will be included.
        Typically, scripts of interest are in transactions with low value.
        spent: Boolean to select only spent or unspent transactions.

    Returns:
        A list with all the scripts from the transactions that fulfill the specified criteria of max_value and spent.
        Note the first 6 and the last 4 bytes are removed in the output.

    """

    scripts = []
    for single_tx in raw_tx['out']:
        if single_tx['value'] <= max_value and single_tx['spent'] is spent:
            scripts.append(single_tx['script'][6:-4])

    return scripts


def collect_multi_out_scripts(tx_list: list, max_value: float = float('inf')) -> list:
    """Function to collect all the scripts from multiple transactions.

    Args:
        tx_list: list with all transactions of interest
        max_value: Allows to set a threshold for the value of each transaction that will be included.
        Typically, scripts of interest are in transactions with low value.

    Returns:
        A list with all the scripts from the transactions.
        Note the first 6 and the last 4 bytes are removed in the output.

    """

    if not isinstance(tx_list, list):
        tx_list = [tx_list]

    scripts = []
    for transaction in tx_list:
        print(f'Fetching scripts from transaction: {transaction}')

        raw_tx = get_transaction(str(transaction))
        if 'error' not in raw_tx:
            scripts = scripts + collect_out_scripts(raw_tx, max_value=max_value)

        time.sleep(1)

    return scripts


def decode_coinbase_script(block_number: int) -> str:
    """Function to convert the input script of the coinbase transaction into ASCII code.

    Args:
        block_number: block number of interest

    Returns:
        The decoded coinbase input script

    """

    raw_block = get_by_block(block_number)
    in_msg, _ = collect_messages(raw_block)

    return util.byte_to_string(decode_hex_message(in_msg[0])[0])[0]
