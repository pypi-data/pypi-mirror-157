import os
import logging
from flask import jsonify
from alephvault.evm_http_storage.core import loop
from alephvault.evm_http_storage.core.decorators import uses_lock
from alephvault.evm_http_storage.schemas.contracts import WORKER_SCHEMA
from alephvault.evm_http_storage.validation import WorkerSettingsValidator
from alephvault.http_storage.types.method_handlers import MethodHandler
from pymongo import MongoClient


LOGGER = logging.getLogger(__name__)


class EventGrabberWorker(MethodHandler):
    """
    An event grabber is a method handler that, taking the contract
    settings, retrieves the blockchain events after the current
    state, processes them, and updates the state in the blockchain.
    """

    def __init__(self, grabber_settings: dict):
        """
        Creates an event grabber handler by using certain events settings.
        :param grabber_settings: The events settings to use.
        """

        validator = WorkerSettingsValidator(WORKER_SCHEMA)
        valid = validator.validate(grabber_settings)
        if not valid:
            raise ValueError(validator.errors)
        self._contracts_settings = validator.document['contracts']
        contract_keys = [contract['handler'].contract_key for contract in self._contracts_settings]
        if len(contract_keys) != len(set(contract_keys)):
            raise ValueError({"contracts": ['repeated contract keys across contract handlers is not allowed']})
        self._gateway_url = os.environ[validator.document['gateway_url_environment_var']]

    @uses_lock
    def __call__(self, client: MongoClient, resource: str, method: str, db: str, collection: str, filter: dict):
        """
        Processes a request to get the last events and process them.
        :param client: The MongoDB client to use.
        :param resource: The name of the related resource. Not used here.
        :param method: The name of the related method. Not used here.
        :param db: The name of the related resource's database.
        :param collection: The name of the related resource's collection.
        :param filter: The filter of the related resource. Not used here.
        :return: A pair of processed element and an HTTP code: 200 if no error, 500 if error.
        """

        processed, error = loop(gateway_url=self._gateway_url, contracts_settings=self._contracts_settings,
                                client=client, cache_db=db, cache_state_collection=collection)
        if error:
            LOGGER.error(f"An error occurred while running the loop: {type(error).__name__} -> {error}")
            return jsonify(processed), 500
        else:
            return jsonify(processed), 200
