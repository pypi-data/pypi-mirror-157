from alephvault.evm_http_storage.methods import EventGrabberWorker
from .common.erc20 import make_evm_erc20_balance_resource
from .common.erc721 import make_evm_erc721_balance_resource
from .common.erc1155 import make_evm_erc1155_balance_resource


def make_evm_resource(worker_settings: dict, db_name: str = 'evm',
                      state_collection_name: str = 'state',
                      state_resource_name: str = "evm-state"):
    """
    Makes a dictionary holding a single resource. This dictionary
    will be validated using the Remote Storage's mongodb validator.
    :param worker_settings: The settings that define the events
      that will be fetched on a work loop.
    :param db_name: The name of the DB to use for the state
      resource. It must satisfy the Remote Storage's rules
      for the MongoDB identifiers.
    :param state_collection_name: The name of the collection
      to use for the state resource. It must satisfy the Remote
      Storage's rules for the MongoDB identifiers.
    :param state_resource_name: The name for the state resource.
    :return: A dictionary with the resource configuration.
    """

    return {
        state_resource_name: {
            "db": db_name,
            "collection": state_collection_name,
            "type": "simple",
            "verbs": ["read"],
            "methods": {
                "grab": {
                    "type": "operation",
                    "handler": EventGrabberWorker(worker_settings)
                }
            },
            "schema": {
                "value": {
                    "type": "dict",
                    "keysrules": {
                        "type": "string",
                        "regex": "[a-zA-Z][a-zA-Z0-9_-]+"
                    },
                    "valuesrules": {
                        "type": "string",
                        "regex": "0x[0-9a-f]{1,64}"
                    }
                }
            }
        }
    }


def make_standard_evm_resources(worker_settings: dict, db_name: str = 'evm',
                                state_collection_name: str = 'state',
                                state_resource_name: str = "evm-state",
                                erc20balance_collection_name: str = 'erc20-balance',
                                erc20balance_resource_name: str = "evm-erc20-balance",
                                erc721balance_collection_name: str = 'erc721-ownership',
                                erc721balance_resource_name: str = "evm-erc721-ownership",
                                erc1155balance_collection_name: str = 'erc1155-ownership',
                                erc1155balance_resource_name: str = "evm-erc1155-ownership"):
    """
    Makes a standard EVM resources set involving: The state table, the ERC-20
    cache table, the ERC-721 cache table, and the ERC-1155 cache table. Those
    3 last tables are just for convenience for standard contracts, but the state
    table is mandatory for this whole system to work.
    :param worker_settings: The settings for the event grabbing worker.
    :param db_name: The name of the EVM db.
    :param state_collection_name: The name of the state collection.
    :param state_resource_name: The resource key for the state.
    :param erc20balance_collection_name: The name of the ERC-20 balances collection.
    :param erc20balance_resource_name: The resource key for the ERC-20 balances.
    :param erc721balance_collection_name: The name of the ERC-721 balances collection.
    :param erc721balance_resource_name: The resource key for the ERC-721 balances.
    :param erc1155balance_collection_name: The name of the ERC-1155 balances collection.
    :param erc1155balance_resource_name: The resource key for the ERC-1155 balances.
    :return: The full resources schema, to be used by a Remote Storage server.
    """

    return {
        **make_evm_resource(worker_settings=worker_settings, db_name=db_name,
                            state_collection_name=state_collection_name,
                            state_resource_name=state_resource_name),
        **make_evm_erc20_balance_resource(db_name=db_name,
                                          erc20balance_collection_name=erc20balance_collection_name,
                                          erc20balance_resource_name=erc20balance_resource_name),
        **make_evm_erc721_balance_resource(db_name=db_name,
                                           erc721balance_collection_name=erc721balance_collection_name,
                                           erc721balance_resource_name=erc721balance_resource_name),
        **make_evm_erc1155_balance_resource(db_name=db_name,
                                            erc1155balance_collection_name=erc1155balance_collection_name,
                                            erc1155balance_resource_name=erc1155balance_resource_name)
    }
