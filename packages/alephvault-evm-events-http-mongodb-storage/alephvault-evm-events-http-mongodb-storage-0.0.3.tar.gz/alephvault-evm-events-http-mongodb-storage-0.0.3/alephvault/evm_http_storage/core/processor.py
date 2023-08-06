import logging

from pymongo import MongoClient
from pymongo.collection import Collection
from web3 import Web3, providers

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def _tohex(value: int):
    """
    Normalizes an integer value to its hexadecimal representation.
    :param value: The value to normalize to hex.
    :return: The normalized hexadecimal value.
    """

    h = hex(value)[2:]
    return "0x" + ("0" * max(0, 64 - len(h))) + h


def process_full_events_list(events_list: dict, contract_settings: dict, client: MongoClient,
                             state_collection: Collection, state: dict, gateway_url: str):
    """
    Processes all the events in the incoming list. This is done according
    to a given current state (and state collection), its state collection
    (to update it appropriately), and a given client to be used into the
    specific event handlers.
    :param events_list: The list of events to process. This is actually a dictionary.
    :param contract_settings: A dictionary with the per-event settings.
    :param client: A MongoDB client.
    :param state_collection: A collection, related to the client, into which
      the state will be saved.
    :param state: The current state, which is periodically updated and pushed.
    :param gateway_url: The gateway url to create a web3 client.
    :return: The events that were effectively synchronized, and whether an exception
      occurred in the processing.
    """

    all_processed_events = []

    try:
        web3 = Web3(providers.HTTPProvider(gateway_url))
        with client.start_session() as session:
            # Inside this session, all the events will be iterated.
            # The first iteration level, which will correspond to
            # a MongoDB Transaction, belongs to the block number.
            for blockNumber in sorted(events_list.keys()):
                with session.start_transaction():
                    # Processes all the events. The events themselves
                    # will NOT be stored directly, but the handlers
                    # MAY cause some data be stored.
                    #
                    # Each event is expected to have the following
                    # fields:
                    # - "args" (a dictionary - it contains data that
                    #   might require normalization). To be processed
                    #   by the handlers.
                    # - "blockNumber": An arbitrary-length integer
                    #   number with the block number. If stored, it
                    #   should be normalized (to hex string).
                    # - "transactionIndex": An arbitrary-length integer
                    #   number, but typically -in practice- in the range
                    #   of 32 bits. If stored, in the future it might
                    #   need of normalization (to hex string).
                    # - "logIndex": An arbitrary-length integer number,
                    #   but typically -in practice- in the range of 32
                    #   bits. If stored, in the future it might need of
                    #   normalization (to hex string).
                    # - "eventKey": A unique event key, among the other
                    #   registered events (which are a combination of
                    #   the event address, the ABI, and the name of the
                    #   event we're interested in retrieving).
                    events = sorted(events_list[blockNumber],
                                    key=lambda evt: (evt['transactionIndex'], evt['logIndex']))
                    processed_events = []
                    for event in events:
                        handler = contract_settings[event['contract-key']]["handler"]
                        response = handler(client, session, event, web3)
                        if response is not None:
                            processed_events.append(response)
                    # Update and store the states.
                    state[event['event-state-key']] = _tohex(blockNumber + 1)
                    state_collection.replace_one({}, {"value": state}, session=session, upsert=True)
                    # Update response.
                    all_processed_events.extend(processed_events)
        return all_processed_events, None
    except Exception as e:
        LOGGER.exception("Error on processor!")
        return all_processed_events, e
