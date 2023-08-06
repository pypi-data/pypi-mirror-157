from typing import List
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from web3 import Web3
from web3.datastructures import AttributeDict
from .abi import ERC1155ABI
from ...contract_handler import ContractHandler


class ERC1155Handler(ContractHandler):
    """
    An ERC-1155 balance handler uses the events to maintain the balances of all the tokens
    in the contract.
    """

    def get_abi(self):
        return ERC1155ABI

    def get_events(self):
        return ["TransferSingle", "TransferBatch"]

    def __init__(self, contract_key: str, db_name: str = 'evm',
                 erc1155balance_collection_name: str = 'erc1155-ownership'):
        super().__init__(contract_key)
        self._db_name = db_name
        self._erc1155balance_collection_name = erc1155balance_collection_name

    def __call__(self, client: MongoClient, session: ClientSession, event: AttributeDict, web3: Web3):
        """
        Intended to process logs which come from a TransferSingle(address indexed, address
        indexed, uint256 token, uint256 amount) and TransferBatch(address indexed, address
        indexed, uint256[] tokens, uint256[] amounts). The address 0x0 will not be taken
        into account (in the 1st argument means "mint", and in the second argument means
        "burn"). The result involves (the addresses, the transferred (token, amount) pairs,
        the final balances of each address on each involved token).
        :param client: The MongoDB client to use.
        :param session: The current MongoDB session.
        :param event: The event being processed.
        :param web3: The current Web3 client - not used here.
        :return: A response that tells the cache updates and event details.
        """

        event_name = event['event']
        args = event['args']
        from_ = self._get_arg(args, 'from')
        to = self._get_arg(args, 'to')
        collection = client[self._db_name][self._erc1155balance_collection_name]

        if event_name == 'TransferSingle':
            id_ = hex(self._get_arg(args, 'id') or 0)
            value = self._get_arg(args, 'value') or 0
            return self._handle_transfer_single(collection, session, from_, to, id_, value)
        elif event_name == 'TransferBatch':
            ids_ = [hex(k) for k in self._get_arg(args, 'ids') or []]
            values = self._get_arg(args, 'values') or []
            return self._handle_transfer_batch(collection, session, from_, to, ids_, values)
        else:
            return {"contract-key": self._contract_key, "from": from_, "to": to, "unexpected_event": True}

    def _handle_transfer_single(self, collection: Collection, session: ClientSession,
                                from_: str, to: str, id_: str, value: int):
        """
        Processes a TransferSingle event, in a similar way to how ERC-20 processes
        its Transfer event, but also telling the token id.
        :param collection: The involved cache collection.
        :param session: The current MongoDB session.
        :param from_: The token sender. It will be zero on mint.
        :param to: The token receiver. It will be zero on burn.
        :param id_: The token id.
        :param value: The token amount.
        :return: A response that tells the cache updates and event details.
        """

        response = {"contract-key": self._contract_key, "from": from_, "to": to, "token": id_}

        if not self._is_zero(from_):
            from_entry = collection.find_one({
                "contract-key": self._contract_key,
                "owner": from_,
                "token": id_
            }, session=session) or {}
            from_balance = int(from_entry.get('amount') or '0')
            from_balance -= value
            from_balance_str = str(from_balance)
            collection.replace_one({
                "contract-key": self._contract_key,
                "owner": from_,
                "token": id_
            }, {
                "contract-key": self._contract_key,
                "owner": from_,
                "token": id_,
                "amount": from_balance_str
            }, session=session, upsert=True)
            response["from_balance"] = from_balance_str
        if not self._is_zero(to):
            to_entry = collection.find_one({
                "contract-key": self._contract_key,
                "owner": to,
                "token": id_
            }, session=session) or {}
            to_balance = int(to_entry.get('amount') or '0')
            to_balance += value
            to_balance_str = str(to_balance)
            collection.replace_one({
                "contract-key": self._contract_key,
                "owner": to,
                "token": id_
            }, {
                "contract-key": self._contract_key,
                "owner": to,
                "token": id_,
                "amount": to_balance_str
            }, session=session, upsert=True)
            response["to_balance"] = to_balance_str
        return response

    def _handle_transfer_batch(self, collection: Collection, session: ClientSession,
                               from_: str, to: str, ids: List[str], values: List[int]):
        """
        Processes a TransferBatch event, which involves per-token updates.
        :param collection: The involved cache collection.
        :param session: The current MongoDB session.
        :param from_: The token sender. It will be zero on mint.
        :param to: The token receiver. It will be zero on burn.
        :param ids: The token ids.
        :param values: The respective token amounts.
        :return: A response that tells the cache updates and event details.
        """

        response = {"contract-key": self._contract_key, "from": from_, "to": to}

        if not self._is_zero(from_):
            from_balances = {}
            for id_, value in zip(ids, values):
                from_entry = collection.find_one({
                    "contract-key": self._contract_key,
                    "owner": from_,
                    "token": id_
                }, session=session) or {}
                from_balance = int(from_entry.get('amount') or '0')
                from_balance -= value
                from_balance_str = str(from_balance)
                collection.replace_one({
                    "contract-key": self._contract_key,
                    "owner": from_,
                    "token": id_
                }, {
                    "contract-key": self._contract_key,
                    "owner": from_,
                    "token": id_,
                    "amount": from_balance_str
                }, session=session, upsert=True)
                from_balances[id_] = from_balance_str
            response["from_balances"] = from_balances
        if not self._is_zero(to):
            to_balances = {}
            for id_, value in zip(ids, values):
                to_entry = collection.find_one({
                    "contract-key": self._contract_key,
                    "owner": to,
                    "token": id_
                }, session=session) or {}
                to_balance = int(to_entry.get('amount') or '0')
                to_balance += value
                to_balance_str = str(to_balance)
                collection.replace_one({
                    "contract-key": self._contract_key,
                    "owner": to,
                    "token": id_
                }, {
                    "contract-key": self._contract_key,
                    "owner": to,
                    "token": id_,
                    "amount": to_balance_str
                }, session=session, upsert=True)
                to_balances[id_] = to_balance_str
            response["to_balances"] = to_balances
        return response
