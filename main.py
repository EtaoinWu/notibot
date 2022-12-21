from configparser import ConfigParser
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
import aiohttp
from aiohttp import web
from datetime import datetime
import html


config = ConfigParser()
config.read("config.ini", encoding="utf-8")

webhook_host = config["webhook"]["hostname"]
webhook_port = config.getint("webhook", "port")

pushsafer_key = config["pushsafer"].get("private_key", None)
pushsafer_icon_map = config["pushsafer_icon_map"]

proxy_dict = None
if config.has_section("proxy"):
    proxy_dict = {
        "scheme": config["proxy"]["scheme"],
        "hostname": config["proxy"]["hostname"],
        "port": int(config["proxy"]["port"]),
        "username": config["proxy"].get("username", None),
        "password": config["proxy"].get("password", None),
    }
    if proxy_dict["username"] is None:
        del proxy_dict["username"]
    if proxy_dict["password"] is None:
        del proxy_dict["password"]


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
        if app in pushsafer_icon_map and pushsafer_key is not None:
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
