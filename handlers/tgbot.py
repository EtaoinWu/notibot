from . import handler
import logging
import pyrogram
from pyrogram import Client, filters, enums
import html

class TelegramBotHandler(handler.Handler):
    """Telegram bot handler"""

    def __init__(self, config):
        if not config:
            config = {}
        self.config = config
        self.bot = None
        

    async def initialize(self):
        logging.debug(f"Initializing with config: {self.config}")
        if self.config is None:
            return
        self.bot = Client(
            "my_bot",
            api_id=self.config["api_id"],
            api_hash=self.config["api_hash"],
            bot_token=self.config["bot_token"],
            proxy=self.config.get('proxy'),
        )
        
        @self.bot.on_message(filters.command("getid"))
        async def getid(client, message):
            await message.reply_text(message.chat.id)

    async def handle(self, payload):
        """Handle request"""
        if self.config is None:
            return
        
        title = payload["title"]
        text = payload["text"]
        app = payload["app"]
        time = payload["time"]
        message = f"<b>{html.escape(title)}</b>\n{html.escape(text)}\n<i>{html.escape(app)},</i> <code>{time}</code>"
        await self.bot.send_message(
            self.config["chat_id"], message, parse_mode=enums.ParseMode.HTML
        )
    
    async def start(self):
        await self.bot.start()
        await pyrogram.idle()
        await self.bot.stop()
        
        