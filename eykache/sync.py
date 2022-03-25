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


def to_event(item):
    return (
        to_int(item["parameters"][0]["value"]),
        to_int(item["parameters"][1]["value"]),
        item["block_number"],
    )


async def start(database, config):

    try:
        with open(config._get_path("data.json"), "r") as read:
            content = json.load(read)
            last_block = content["last_block"]
    except FileNotFoundError:
        last_block = 0

    async with aiohttp.ClientSession() as session:
        url = f"{config.endpoint}?chain_id={config.chain_id}&contract={config.contract}&from_block={last_block}&size={config.page_size}&name=world_update"
        print("[Info] Fetching Eykar contract events...")
        response = await session.get(f"{url}&page=1")
        parsed = await response.json()
        to_do = parsed["total"] - config.page_size
        for item in parsed["items"]:
            x, y, block = to_event(item)
        for i in range(2, to_do // config.page_size + 2):
            response = await session.get(f"{url}&page={i}")
            parsed = await response.json()
            for item in parsed["items"]:
                x, y, block = to_event(item)

        with open(config._get_path("data.json"), "w") as write:

            json.dump({"last_block": block}, write)

        """"
        last_page = parsed["lastPage"]
        items = parsed["items"]
        events = {}
        missing = []
        done = False
        for event in items:
            identifier = event["id"]
            if identifier <= last_id:
                done = True
                break
            async with session.get(
                f"https://goerli.voyager.online/api/event/{identifier}"
            ) as event:
                json_event = await event.json()
                if json_event:
                    x, y = json_event["data"]
                    events[identifier] = (to_int(x), to_int(y))
                else:
                    missing.append(identifier)

        if not done:
            for i in range(2, last_page + 1):
                hash_events = await fetch_items(session, config, i)
                for event_id, value in hash_events.items():
                    if event_id < last_id:
                        break
                    events[event_id] = value


        """
