import web3


def grab_all_events_since(gateway_url: str, contracts_settings: list, state: dict):
    """
    Grabs all the events since a certain limit, per state.
    :param gateway_url: The URL of the gateway to use (it must support event logs retrieval).
    :param contracts_settings: The list with the settings to use.
    :param state: The state (a mapping of eventKey => startBlock) to use.
    :return: A dictionary of blockNumber => events.
    """

    client = web3.Web3(web3.providers.HTTPProvider(gateway_url))
    events_list = {}
    for contract_settings in contracts_settings:
        handler = contract_settings['handler']
        contract_key = handler.contract_key
        contract = client.eth.contract(web3.Web3.toChecksumAddress(contract_settings['address']),
                                       abi=handler.get_abi())
        for event_name in handler.get_events():
            event_state_key = f"{contract_key}:{event_name}"
            event_filter = getattr(contract.events, event_name).createFilter(
                fromBlock=state.get(event_state_key, '0x0')
            )
            for event in event_filter.get_all_entries():
                entry = {**{
                   k: v for k, v in event.items() if k in {"blockNumber", "transactionIndex", "logIndex", "args",
                                                           "event"}
                }, "event-state-key": event_state_key, "contract-key": contract_key}
                events_list.setdefault(entry["blockNumber"], []).append(entry)
    return events_list
