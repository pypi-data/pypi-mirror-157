from pymongo import MongoClient
from pymongo.client_session import ClientSession
from web3 import Web3
from web3.datastructures import AttributeDict


class ContractHandler:
    """
    A handler for a given contract's events being received.
    It will take into account 3 things when an event is received:
    a client, a session (within that client), and an event log
    to process. It also knows which ABI to use.
    """

    def _is_zero(self, value):
        """
        Tests whether a value is a numeric 0 or 0.0, or perhaps
        a string representation of a 0 numeric value in any base.
        :param value: The value to test.
        :return: Whether it is zero or not.
        """

        if value == 0:
            return True

        for b in range(2, 37):
            try:
                if int(value, b) == 0:
                    return True
                else:
                    break
            except:
                pass

        return False

    def _get_arg(self, args, key):
        """
        Gets an argument from the args, by trying both `{key}` and `_{key}`
        as the key to test.
        :param args: The args to get an argument from
        :param key:
        :return:
        """

        if key in args:
            return args[key]
        else:
            return args.get("_" + key)

    def get_abi(self):
        """
        Returns the ABI that this contract handler will use.
        :return: The ABI, as a list.
        """

        raise NotImplementedError

    def get_events(self):
        """
        The list of events supported by this contract handler's ABI.
        :return: The list of events.
        """

        # If we happen to be interested in all the events
        # we could instead uncomment the next line:
        # return [entry['name'] for entry in self.get_abi() if entry.get('type') == 'event']
        raise NotImplementedError

    @property
    def contract_key(self):
        """
        The handler's contract key.
        """

        return self._contract_key

    def __init__(self, contract_key: str):
        """
        Each handler will be initialized with a contract key.
        :param contract_key: The handler's contract key.
        """

        self._contract_key = contract_key

    def __call__(self, client: MongoClient, session: ClientSession, event: AttributeDict, web3: Web3):
        """
        Processes an event inside a transaction. That transaction exists in a session,
        which is turn belongs to the client, and the given event will be processed by
        said transaction. This handler must process whatever it needs as given (e.g.
        for ERC-20 Transfer event, increment and decrement existing quantities, save
        for the fact of 0x0 addresses), and return whatever makes sense for the game
        to be notified about the changes.
        :param client: The MongoDB client to use.
        :param session: The current MongoDB session.
        :param event: The event being processed.
        :param web3: The Web3 client to use (optional).
        :return: Whatever makes sense for the game.
        """

        raise NotImplementedError
