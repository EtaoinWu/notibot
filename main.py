import yaml
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
import aiohttp
from aiohttp import web
from datetime import datetime
import html

# load from config.yaml
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

webhook_host = config["webhook"]["hostname"]
webhook_port = config["webhook"]["port"]

pushsafer_key = config["pushsafer"].get("private_key", None) if config["pushsafer"] else None
pushsafer_icon_map = config["pushsafer_icon_map"]

proxy_dict = None
if "proxy" in config:
    proxy_dict = config["proxy"]


async def main():
    pushsafer_session = aiohttp.ClientSession('https://www.pushsafer.com')

    tg = Client(
        "my_bot",
        api_id=config["pyrogram"]["api_id"],
        api_hash=config["pyrogram"]["api_hash"],
        bot_token=config["pyrogram"]["bot_token"],
        proxy=proxy_dict,
    )

    @tg.on_message(filters.command("getid"))
    async def getid(client, message):
        await message.reply_text(message.chat.id)

    http = web.Application()
    routes = web.RouteTableDef()

    @routes.get("/")
    async def hello(request):
        return web.Response(text="Hello, world")

    @routes.post("/new_notification" + config["webhook"]["token"])
    async def new_notification(request):
        json = await request.json()
        title = json["title"]
        text = json["text"]
        app = json["app"]
        time = datetime.fromtimestamp(int(json["time"]) // 1000)
        message = f"<b>{html.escape(title)}</b>\n{html.escape(text)}\n<i>{html.escape(app)},</i> <code>{time}</code>"
        print(message)
        await tg.send_message(
            config["pyrogram"]["chat_id"], message, parse_mode=enums.ParseMode.HTML
        )
        if pushsafer_key is not None and app in pushsafer_icon_map:
            async with pushsafer_session.post(
                "/api",
                data={
                    "k": pushsafer_key,
                    "t": f"[{app}] {title}",
                    "m": text,
                    "i": pushsafer_icon_map.get(app, 1),
                    "d": "a",
                    "s": "0",
                },
            ) as resp:
                print(resp.status)
        return web.Response(text="OK")

    http.add_routes(routes)
    runner = web.AppRunner(http)
    await runner.setup()
    site = web.TCPSite(runner, webhook_host, webhook_port)
    await site.start()

    await tg.start()
    await pyrogram.idle()
    await tg.stop()

try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

asyncio.run(main())
