import logging

from pymongo import MongoClient
from .grabber import grab_all_events_since
from .processor import process_full_events_list


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def loop(gateway_url: str, contracts_settings: list, client: MongoClient,
         cache_db: str, cache_state_collection: str):
    """
    The whole work loop, including the state retrieval and the full
      event processing and update. The order is the following: Get
      the current state, if any; retrieve all the events related to
      that state; and process those elements accordingly (block by
      block). Then return all the successfully processed events,
      and whether an error occurred in the middle. The state will
      be consistently stored.
    :param gateway_url: The URL of the gateway to use (it must support
      event logs retrieval).
    :param contracts_settings: The dictionary with the settings to use.
    :param client: A MongoDB client.
    :param cache_db: The db that will be related to this cache feature.
    :param cache_state_collection: The collection, inside the db
      used as cache, that will hold the current state.
    :return: A list of successfully processed events, and whether
      an error occurred or not in that processing.
    """

    state_collection = client[cache_db][cache_state_collection]
    state = (state_collection.find_one({}) or {}).get('value', {})
    LOGGER.info(f"loop::Using state: {state} against gateway: {gateway_url}")
    events_list = grab_all_events_since(gateway_url, contracts_settings, state)
    LOGGER.info(f"loop::Processing events ({len(events_list)})")
    return process_full_events_list(events_list, {cs['handler'].contract_key: cs for cs in contracts_settings},
                                    client, state_collection, state, gateway_url)
