from flask import request
from cerberus import Validator
from pymongo import MongoClient
from alephvault.http_storage.core.responses import format_invalid, ok
from alephvault.http_storage.types.method_handlers import MethodHandler
from alephvault.evm_http_storage.core.decorators import uses_lock


class ERC20BalanceOf(MethodHandler):
    """
    Gets the balance of an account in an ERC-20 contract. If no balance is found, this returns 0.
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
        }
    }

    @uses_lock
    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        validator = Validator(self.SCHEMA)
        if not validator.validate(request.args):
            return format_invalid(validator.errors)
        entry = client[db][collection].find_one({**filter, "owner": validator.document["owner"],
                                                 "contract-key": validator.document["contract-key"]})
        return ok({"amount": (entry or {}).get("amount", 0)})


class ERC20Balances(MethodHandler):
    """
    Gets all the balances of an ERC-20 contract, by paging.
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
        return ok([{"owner": e.get("owner"), "amount": e.get("amount")} for e in query])


class ERC20Reset(MethodHandler):
    """
    Resets the state for certain event(s) of an ERC-20 contract.
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
        state.pop(f"{contract_key}:Transfer", None)
        state_collection.replace_one({}, {"value": state}, upsert=True)
        return ok()
