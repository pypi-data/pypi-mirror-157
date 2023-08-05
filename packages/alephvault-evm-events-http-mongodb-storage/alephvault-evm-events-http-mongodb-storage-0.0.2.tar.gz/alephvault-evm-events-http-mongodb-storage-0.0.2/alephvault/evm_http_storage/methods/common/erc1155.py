from flask import request
from cerberus import Validator
from pymongo import MongoClient
from alephvault.http_storage.core.responses import format_invalid, ok
from alephvault.http_storage.types.method_handlers import MethodHandler
from alephvault.evm_http_storage.core.decorators import uses_lock


class ERC1155BalanceOf(MethodHandler):
    """
    Gets the balance of a token for an account in an ERC-1155 contract.
    """

    SCHEMA = {
        "contract-key": {
            "type": "string",
            "required": True
        },
        "owner": {
            "type": "string",
            "required": True,
            "regex": r"0x[a-fA-F0-9]{40}"
        },
        "token": {
            "type": "string",
            "required": True,
            "regex": "0x[a-f0-9]{1,64}"
        }
    }

    @uses_lock
    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        validator = Validator(self.SCHEMA)
        if not validator.validate({**request.args}):
            return format_invalid(validator.errors)
        entry = client[db][collection].find_one({**filter, "contract-key": validator.document["contract-key"],
                                                 "owner": validator.document["owner"],
                                                 "token": validator.document["token"]})
        return ok({"amount": (entry or {}).get("amount", 0)})


class ERC1155BalancesOf(MethodHandler):
    """
    Gets the balances of all the tokens for an account in an ERC-1155 contract.
    """

    SCHEMA = {
        "contract-key": {
            "type": "string",
            "required": True
        },
        "owner": {
            "type": "string",
            "required": True,
            "regex": r"0x[a-fA-F0-9]{40}"
        },
        "offset": {
            "type": "string",
            "required": True,
            "regex": r"\d+",
            "default": "0"
        },
        "limit": {
            "type": "string",
            "required": True,
            "regex": r"0*[1-9]\d*",
            "default": "20"
        }
    }

    @uses_lock
    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        validator = Validator(self.SCHEMA)
        if not validator.validate({**request.args}):
            return format_invalid(validator.errors)
        query = client[db][collection].find({**filter, "contract-key": validator.document["contract-key"],
                                             "owner": validator.document["owner"]})
        query = query.skip(int(validator.document["offset"])).limit(int(validator.document["limit"]))
        return ok([{"token": e.get("token"), "amount": e.get("amount")} for e in query])


class ERC1155Balances(MethodHandler):
    """
    Gets the balances of all the tokens and accounts in an ERC-1155 contract, by paging.
    """

    SCHEMA = {
        "contract-key": {
            "type": "string",
            "required": True
        },
        "offset": {
            "type": "string",
            "required": True,
            "regex": r"\d+",
            "default": "0"
        },
        "limit": {
            "type": "string",
            "required": True,
            "regex": r"0*[1-9]\d*",
            "default": "20"
        }
    }

    @uses_lock
    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        validator = Validator(self.SCHEMA)
        if not validator.validate({**request.args}):
            return format_invalid(validator.errors)
        query = client[db][collection].find({**filter, "contract-key": validator.document["contract-key"]})
        query = query.skip(int(validator.document["offset"])).limit(int(validator.document["limit"]))
        return ok([{"token": e.get("token"), "owner": e.get("owner"), "amount": e.get("amount")} for e in query])


class ERC1155Reset(MethodHandler):
    """
    Resets the state for certain event(s) of an ERC1155 contract.
    """

    SCHEMA = {
        "contract-key": {
            "type": "string",
            "required": True
        }
    }

    def __init__(self, state_db_name: str, state_collection_name: str):
        self._state_db_name = state_db_name
        self._state_collection_name = state_collection_name

    @uses_lock
    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        validator = Validator(self.SCHEMA)
        if not validator.validate({**request.args}):
            return format_invalid(validator.errors)
        contract_key = validator.document["contract-key"]
        state_collection = client[self._state_db_name][self._state_collection_name]
        cache_collection = client[db][collection]
        cache_collection.delete_many({"contract-key": contract_key})
        state = (state_collection.find_one({}) or {}).get("value", {})
        state.pop(f"{contract_key}:TransferSingle", None)
        state.pop(f"{contract_key}:TransferBatch", None)
        state_collection.replace_one({}, {"value": state}, upsert=True)
        return ok()
