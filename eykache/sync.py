import aiohttp
import asyncio
import json


def to_int(felt):
    P = 2**251 + 17 * 2**192 + 1
    number = int(felt, 16) if felt.startswith("0x") else int(felt)
    if abs(number - P) < number:
        return number - P
    else:
        return number


def to_felt(integer):
    P = 2**251 + 17 * 2**192 + 1
    if integer >= 0:
        return integer % P
    else:
        return integer + P


def to_event(item):
    return (
        to_int(item["parameters"][0]["value"]),
        to_int(item["parameters"][1]["value"]),
        item["block_number"],
    )

def claim(database, x, y, colony):
    database.write(x, y, colony)
    print(f"- colony {colony} claimed ({x},{y})")

async def start(database, eykar, config):

    try:
        with open(config._get_path("data.json"), "r") as read:
            content = json.load(read)
            last_block = content["last_block"]
    except FileNotFoundError:
        last_block = 0

    async with aiohttp.ClientSession() as session:
        url = f"{config.endpoint}?chain_id={config.chain_id}&contract={config.contract}&from_block={last_block+1}&size={config.page_size}&name=world_update"
        print("[Info] Fetching new Eykar contract events...")
        response = await session.get(f"{url}&page=1")
        parsed = await response.json()
        if not "detail" in parsed or parsed["detail"] != "Not Found":
            to_do = parsed["total"] - config.page_size
            for item in parsed["items"]:
                x, y, block = to_event(item)
                colony, _, _ = await eykar.get_plot(to_felt(x), to_felt(y))
                claim(database, x, y, colony)
            for i in range(2, to_do // config.page_size + 2):
                response = await session.get(f"{url}&page={i}")
                parsed = await response.json()
                for item in parsed["items"]:
                    x, y, block = to_event(item)
                    colony, _, _ = await eykar.get_plot(to_felt(x), to_felt(y))
                    claim(database, x, y, colony)

            with open(config._get_path("data.json"), "w") as write:
                json.dump({"last_block": block}, write)
            database.commit()

        print("[Info] Finished fetching new Eykar contract events")
