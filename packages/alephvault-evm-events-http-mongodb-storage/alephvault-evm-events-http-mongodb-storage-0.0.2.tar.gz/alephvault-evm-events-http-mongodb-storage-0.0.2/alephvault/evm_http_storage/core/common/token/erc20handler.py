from pymongo import MongoClient
from pymongo.client_session import ClientSession
from web3 import Web3
from web3.datastructures import AttributeDict
from .abi import ERC20ABI
from ...contract_handler import ContractHandler


class ERC20Handler(ContractHandler):
    """
    An ERC-20 balance handler uses the events to maintain the balance cache.
    """

    def get_abi(self):
        return ERC20ABI

    def get_events(self):
        return ["Transfer"]

    def __init__(self, contract_key: str, db_name: str = 'evm', erc20balance_collection_name: str = 'erc20-balance'):
        super().__init__(contract_key)
        self._db_name = db_name
        self._erc20balance_collection_name = erc20balance_collection_name

    def __call__(self, client: MongoClient, session: ClientSession, event: AttributeDict, web3: Web3):
        """
        Intended to process event logs which come from a Transfer(address indexed, address indexed, uint256)
        event. The address 0x0 will not be taken into account (in the 1st argument means "mint", and in the
        second argument means "burn"). The result involves the transferred amount, the addresses, and the
        current balances of each of the non-0x0 involved accounts (into keys "from_balance" and "to_balance").
        :param client: The MongoDB client to use.
        :param session: The current MongoDB session.
        :param event: The event being processed.
        :param web3: The current Web3 client - not used here.
        :return: Whatever makes sense for the game.
        """

        args = event['args']
        from_ = self._get_arg(args, 'from')
        to = self._get_arg(args, 'to')
        value = self._get_arg(args, 'value')
        collection = client[self._db_name][self._erc20balance_collection_name]

        if event["event"] != "Transfer":
            return {"contract-key": self._contract_key, "from": from_, "to": to, "unknown_event": True}

        response = {"contract-key": self._contract_key, "from": from_, "to": to, "value": str(value)}
        if not self._is_zero(from_):
            from_entry = collection.find_one({
                "contract-key": self._contract_key,
                "owner": from_
            }, session=session) or {}
            from_balance = int(from_entry.get('amount') or '0')
            from_balance -= value
            from_balance_str = str(from_balance)
            collection.replace_one({
                "contract-key": self._contract_key,
                "owner": from_
            }, {
                "contract-key": self._contract_key,
                "owner": from_,
                "amount": from_balance_str
            }, session=session, upsert=True)
            response["from_balance"] = from_balance_str
        if not self._is_zero(to):
            to_entry = collection.find_one({
                "contract-key": self._contract_key,
                "owner": to
            }, session=session) or {}
            to_balance = int(to_entry.get('amount') or '0')
            to_balance += value
            to_balance_str = str(to_balance)
            collection.replace_one({
                "contract-key": self._contract_key,
                "owner": to
            }, {
                "contract-key": self._contract_key,
                "owner": to,
                "amount": to_balance_str
            }, session=session, upsert=True)
            response["to_balance"] = to_balance_str
        return response
