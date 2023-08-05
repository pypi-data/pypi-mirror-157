from .erc1155handler import ERC1155Handler
from .erc20handler import ERC20Handler
from .erc721handler import ERC721Handler


def erc20_schema_entry(address: str, contract_key: str):
    """
    Creates a contract entry for an ERC-20 contract.
    :param address: The contract address.
    :param contract_key: The key to associate to this contract.
    :return: The contract's schema entry.
    """

    return {
        'address': address,
        'handler': ERC20Handler(contract_key)
    }


def erc721_schema_entry(address: str, contract_key: str):
    """
    Creates a contract entry for an ERC-721 contract.
    :param address: The contract address.
    :param contract_key: The key to associate to this contract.
    :return: The contract's schema entry.
    """

    return {
        'address': address,
        'handler': ERC721Handler(contract_key)
    }


def erc1155_schema_entry(address: str, contract_key: str):
    """
    Creates a contract entry for an ERC-1155 contract.
    :param address: The contract address.
    :param contract_key: The key to associate to this contract.
    :return: The contract's schema entry.
    """

    return {
        'address': address,
        'handler': ERC1155Handler(contract_key)
    }
