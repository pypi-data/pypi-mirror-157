import logging
from alephvault.http_storage.flask_app import StorageApp
from alephvault.evm_http_storage.core.common.token.shortcuts import erc20_schema_entry, erc721_schema_entry, \
    erc1155_schema_entry
from alephvault.evm_http_storage.schemas.resources import make_standard_evm_resources

logging.basicConfig()

# These are only sample values in a sample deployment.
ERC1155 = "0x83fD6d68C21c5a646971F8a788f3992365321304"
ERC721 = "0x0d938498e6C47DCc1c5a59Abc8aEf0eab7D115f4"
ERC20 = "0xb6eFBbc5466693166E25F17998ec0A90263C5582"

RESOURCES = make_standard_evm_resources({
    'contracts': [
        erc20_schema_entry(ERC20, 'erc20-sample'),
        erc721_schema_entry(ERC721, 'erc721-sample'),
        erc1155_schema_entry(ERC1155, 'erc1155-sample')
    ]
})


class SampleStorageApp(StorageApp):
    SETTINGS = {
        "auth": {
            "db": "auth-db",
            "collection": "api-keys"
        },
        "connection": "mongodb+srv://dev-admin:6JzaxJ7jT0WNh2Zk@primal-spark.p4o5k.mongodb.net/",
        "resources": RESOURCES
    }

    def __init__(self, import_name: str = __name__):
        super().__init__(self.SETTINGS, import_name=import_name)
        try:
            self._client["auth-db"]["api-keys"].insert_one({"api-key": "abcdef"})
        except:
            pass


if __name__ == "__main__":
    app = SampleStorageApp()
    app.run("localhost", 6666)
