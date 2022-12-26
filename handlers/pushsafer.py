from . import handler
import aiohttp
import logging

class PushsaferHandler(handler.Handler):
    """Pushsafer handler"""

    def __init__(self, config):
        if not config:
            config = {}
        self.config = config
        self.key = config.get("private_key", None)
        self.icon_map = config.get("icon_map", {})
        self.session = None

    async def initialize(self):
        logging.debug(f"Initializing with config: {self.config}")
        self.session = aiohttp.ClientSession('https://www.pushsafer.com')
    
    async def handle(self, payload):
        """Handle request"""
        if self.key is None:
            return
        
        title = payload["title"]
        text = payload["text"]
        app = payload["app"]
        
        if app not in self.icon_map:
            return
        
        async with self.session.post(
            "/api",
            data={
                "k": self.key,
                "t": f"[{app}] {title}",
                "m": text,
                "i": self.icon_map.get(app, 1),
                "d": "a",
                "s": "0",
            },
        ) as resp:
            logging.info(f"response status: {resp.status}")
