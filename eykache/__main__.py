from config import Config
from aiohttp import web
import server
import asyncio
import sync


async def main():
    conf = Config()
    await sync.start(None, conf)
    app = web.Application(client_max_size=conf.request_max_size)
    server.setup(app, conf, None)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, port=conf.port).start()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(main())
loop.run_forever()
