from pymongo import MongoClient
from pymongo.client_session import ClientSession
from web3 import Web3
from web3.datastructures import AttributeDict
from .abi import ERC721ABI
from ...contract_handler import ContractHandler


class ERC721Handler(ContractHandler):
    """
    An ERC-721 balance handler uses the events to maintain the ownership of the tokens.
    """

    def get_abi(self):
        return ERC721ABI

    def get_events(self):
        return ["Transfer"]

    def __init__(self, contract_key: str, db_name: str = 'evm',
                 erc721balance_collection_name: str = 'erc721-ownership'):
        super().__init__(contract_key)
        self._db_name = db_name
        self._erc721balance_collection_name = erc721balance_collection_name

    def __call__(self, client: MongoClient, session: ClientSession, event: AttributeDict, web3: Web3):
        """
        Intended process event logs which come from a Transfer(address indexed, address indexed, uint256)
        event. The address 0x0 will not be taken into account (in the 1st argument means "mint", and in the
        second argument means "burn"). The result involves the transferred token, and the two addresses.
        :param client: The MongoDB client to use.
        :param session: The current MongoDB session.
        :param event: The event being processed.
        :param web3: The current Web3 client - not used here.
        :return: Whatever makes sense for the game.
        """

        args = event['args']
        from_ = self._get_arg(args, 'from')
        to = self._get_arg(args, 'to')
        token_id = hex(self._get_arg(args, 'tokenId') or 0)
        collection = client[self._db_name][self._erc721balance_collection_name]

        if event["event"] != "Transfer":
            return {"contract-key": self._contract_key, "from": from_, "to": to, "unknown_event": True}

        response = {"contract-key": self._contract_key, "from": from_, "to": to, "tokenId": token_id}
        if not self._is_zero(from_):
            collection.delete_one({
                "contract-key": self._contract_key,
                "owner": from_,
                "token": token_id
            }, session=session)
            response["from_ownership"] = False
        if not self._is_zero(to):
            collection.replace_one({
                "contract-key": self._contract_key,
                "owner": to,
                "token": token_id
            }, {
                "contract-key": self._contract_key,
                "owner": to,
                "token": token_id
            }, session=session, upsert=True) or {}
            response["to_ownership"] = True
        return response
