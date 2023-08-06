import asyncio
from contextlib import asynccontextmanager


class AppLifespan:
    def __init__(self, app):
        self.app = app

    async def __aenter__(self):
        self.send_queue = asyncio.Queue()
        self.receive_queue = asyncio.Queue()
        self.task = asyncio.create_task(self.lifespan())
        await self.wait_startup()

    async def __aexit__(self, *args) -> None:
        await self.wait_shutdown()

    async def lifespan(self):
        scope = {'type': 'lifespan'}
        try:
            await self.app(scope, self.receive_queue.get, self.send_queue.put)
        finally:
            await self.send_queue.put(None)

    async def wait_startup(self):
        await self.receive_queue.put({'type': 'lifespan.startup'})
        message = await self.send_queue.get()
        assert message['type'] in (
            'lifespan.startup.complete',
            'lifespan.startup.failed',
        )
        if message['type'] == 'lifespan.startup.failed':
            message = await self.send_queue.get()
            if message is None:
                self.task.result()

    async def wait_shutdown(self):
        await self.receive_queue.put({'type': 'lifespan.shutdown'})
        message = await self.send_queue.get()
        if message is None:
            self.task.result()
        assert message['type'] == 'lifespan.shutdown.complete'
        await self.task


@asynccontextmanager
async def mock_lifespan():
    yield
