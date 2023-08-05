"""
These schemas define the configuration of contract settings.
Each setting a contract address (a valid, but not checksum
  verified, hexadecimal address), and the handler that will
  be used to process each event in the list of events of a
  given block (that handler also knows and retrieves the
  events that it supports, and the overall ABI).
"""


CONTRACT = {
    "address": {
        "type": "string",
        "required": True,
        "regex": "0x[a-fA-F0-9]{40}"
    },
    "handler": {
        "type": "event-handler",
        "required": True
    }
}


CONTRACTS_SETTINGS = {
    "type": "list",
    "empty": False,
    "schema": {
        "type": "dict",
        "schema": CONTRACT
    }
}


# This schema is meant for the worker loop. It will be
# validated with the WorkerSettingsValidator class.
WORKER_SCHEMA = {
    "contracts": CONTRACTS_SETTINGS,
    "gateway_url_environment_var": {
        "type": "string",
        "required": True,
        "regex": r"[a-zA-Z_][a-zA-Z0-9_]+",  # The url itself will satisfy: r"https?://[\w_-]+(\.[\w_-]+)*(:\d+)/?"
        "default": "GATEWAY_URL"
    }
}
