from config import Config
from aiohttp import web
from db import Database
from contract import Eykar
import server
import asyncio
import sync

async def main():
    conf = Config()
    app = web.Application(client_max_size=conf.request_max_size)
    database = Database(conf)
    eykar = Eykar(conf)
    await eykar.load()
    server.setup(app, conf, database)
    await sync.start(database, eykar, conf)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, port=conf.port).start()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(main())
loop.run_forever()
