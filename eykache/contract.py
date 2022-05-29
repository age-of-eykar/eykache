from starknet_py.contract import Contract
from starknet_py.net.client import Client


class Eykar:
    def __init__(self, config) -> None:
        self.address = config.contract

    async def load(self):
        self.contract = await Contract.from_address(self.address, Client("testnet"))

    async def get_plot(self, x, y):
        (result,) = await self.contract.functions["get_plot"].call(x, y)
        owner, data, structure = (
            result["owner"],
            result["dateOfOwnership"],
            result["structure"],
        )
        return owner, data, structure
