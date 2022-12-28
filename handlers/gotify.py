from . import handler
import aiohttp
import logging

class GotifyHandler(handler.Handler):
    """Gotify handler"""

    def __init__(self, config):
        if not config:
            config = {}
        self.config = config
        self.url = config.get("url")
        self.token = config.get("token")
        self.priority = config.get("priority", {})
        self.session = None

    async def initialize(self):
        logging.debug(f"Initializing with config: {self.config}")
        self.session = aiohttp.ClientSession(
            self.url,
            headers={"X-Gotify-Key": self.token}, timeout=aiohttp.ClientTimeout(total=10)
        )
    
    async def handle(self, payload):
        """Handle request"""
        if self.token is None:
            return

        if type is not None:
            return
        
        title = payload["title"]
        text = payload["text"]
        app = payload["app"]
        
        if app not in self.priority:
            return

        async with self.session.post(
            "/message",
            json={
                "title": f"[{app}] {title}",
                "message": text,
                "priority": self.priority[app],
            },
        ) as resp:
            logging.info(f"response[{resp.status}]: {await resp.text()}")
