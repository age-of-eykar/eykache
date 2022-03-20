import aiohttp
import asyncio
import json


def to_int(felt):
    P = 2**251 + 17 * 2**192 + 1
    number = int(felt)
    if abs(number - P) < number:
        return number - P
    else:
        return number


def add_events(events, items):
    for item in items:
        events[item["event"]] = item


async def fetch_items(session, config, page):
    async with session.get(
        f"{config.endpoint}?contract={config.contract}&ps={config.page_size}&p={page}"
    ) as resp:
        hash_events = {}
        for event in (await resp.json())["items"]:
            identifier = event["id"]
            async with session.get(
                f"https://goerli.voyager.online/api/event/{identifier}"
            ) as event:
                json_event = await event.json()
                x, y = json_event["data"]
                hash_events[identifier] = (to_int(x), to_int(y))
        return hash_events


async def start(database, config):

    try:
        with open(config._get_path("data.json"), "r") as read:
            content = json.load(read)
            last_id = content["last_id"]
    except FileNotFoundError:
        last_id = 0

    async with aiohttp.ClientSession() as session:
        url = f"{config.endpoint}?contract={config.contract}&ps={config.page_size}"
        response = await session.get(f"{url}&p=1")
        parsed = await response.json()
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

            with open(config._get_path("data.json"), "w") as write:
                last_id = next(iter(events))
                json.dump({"last_id": last_id}, write)

        return events
