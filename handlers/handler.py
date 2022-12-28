import abc

class Handler(abc.ABC):
    """Abstract class for handlers"""

    @abc.abstractmethod
    async def initialize(self):
        """Initialize handler"""
        pass

    @abc.abstractmethod
    async def handle(self, payload, type = None):
        """Handle request"""
        pass