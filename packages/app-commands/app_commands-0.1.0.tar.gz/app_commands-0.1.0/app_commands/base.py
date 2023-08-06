import asyncio
import sys
import typing

import click

from app_commands.lifespan import AppLifespan, mock_lifespan
from app_commands.termcolors import OutputWrapper

try:
    import aio_tiny_healthcheck
except ImportError:
    aio_tiny_healthcheck = None


MethodReturnsBool = typing.Union[
    typing.Callable[..., bool],
    typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, bool]],
]


class CommandError(Exception):
    pass


class BaseCommand:
    help = None
    allow_extra_args = False

    lifespan = False
    healthcheck_port = None
    healthcheck_path = '/healthcheck'

    def __init__(
        self,
        app=None,
        stdout=None,
        stderr=None,
        lifespan=None,
        healthcheck=None,
    ):
        self.app = app
        self.stdout = stdout or OutputWrapper(sys.stdout)
        self.stderr = stderr or OutputWrapper(sys.stderr)
        if lifespan is not None:
            self.lifespan = lifespan
        if healthcheck is not None:
            self.healthcheck_port = healthcheck
        self.command_name = getattr(self, 'command_name', '')

    def _lifespan(self):
        if self.app and self.lifespan:
            return AppLifespan(self.app)
        else:
            return mock_lifespan()

    async def _start_healthcheck_server(self):
        if self.healthcheck_port is None:
            return
        assert (
            aio_tiny_healthcheck is not None
        ), 'Requires aio_tiny_healthcheck to be installed'
        checker = aio_tiny_healthcheck.Checker()
        healthchecks = await self.get_healthchecks()
        for name, func in healthchecks.items():
            checker.add_check(name, func)
        hc_server = aio_tiny_healthcheck.HttpServer(
            healthcheck_provider=checker,
            path=self.healthcheck_path,
            port=self.healthcheck_port,
        )
        asyncio.create_task(hc_server.run())

    async def run(self, *args, **kwargs):
        async with self._lifespan():
            await self.startup()
            await self._start_healthcheck_server()
            try:
                await self.handle(*args, **kwargs)
            except CommandError as exc:
                self.stderr.write(str(exc))
                sys.exit(1)
            finally:
                await self.shutdown()

    @classmethod
    def get_click_parameters(cls) -> typing.List[click.Parameter]:
        return []

    async def handle(self, *args, **kwargs):
        raise NotImplementedError

    async def startup(self):
        pass

    async def shutdown(self):
        pass

    async def get_healthchecks(self) -> typing.Mapping[str, MethodReturnsBool]:
        """Returns a dict which maps to methods that will be called on health check."""
        return {}
