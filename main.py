import yaml
import asyncio
import pyrogram
import aiohttp
from aiohttp import web
from datetime import datetime
import html
import logging
from handlers import pushsafer, tgbot

logging.basicConfig(
    level=logging.INFO, format="[{filename} @ {asctime}] {levelname}: {message}", style='{',
)

# load from config.yaml
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

webhook_host = config["webhook"]["hostname"]
webhook_port = config["webhook"]["port"]

pushsafer_handler = pushsafer.PushsaferHandler(config["pushsafer"])
telegram_handler = tgbot.TelegramBotHandler(config["telegram"])
handlers = [pushsafer_handler, telegram_handler]

async def main():
    await pushsafer_handler.initialize()
    await telegram_handler.initialize()

    http = web.Application()
    routes = web.RouteTableDef()

    @routes.get("/")
    async def hello(request):
        return web.Response(text="Hello, world")

    @routes.post("/new_notification" + config["webhook"]["token"])
    async def new_notification(request):
        json = await request.json()
        json["time"] = datetime.fromtimestamp(int(json["time"]) // 1000)
        for handler in handlers:
            await handler.handle(json)
        return web.Response(text="OK")

    http.add_routes(routes)
    runner = web.AppRunner(http)
    await runner.setup()
    site = web.TCPSite(runner, webhook_host, webhook_port)
    await site.start()

    await telegram_handler.start()

try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

asyncio.run(main())
