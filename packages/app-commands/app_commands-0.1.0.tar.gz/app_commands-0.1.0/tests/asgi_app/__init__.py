from starlette.applications import Starlette

app = Starlette()


def run_sync_startup():
    pass


def run_sync_shutdown():
    pass


async def run_async_startup():
    pass


async def run_async_shutdown():
    pass


app.add_event_handler('startup', run_sync_startup)
app.add_event_handler('shutdown', run_sync_shutdown)

app.add_event_handler('startup', run_async_startup)
app.add_event_handler('shutdown', run_async_shutdown)
