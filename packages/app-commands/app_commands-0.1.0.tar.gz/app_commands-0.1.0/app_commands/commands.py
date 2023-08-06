import asyncio
import importlib
import inspect
import pkgutil
import sys
from functools import partial

import click

from app_commands.base import BaseCommand
from app_commands.handlers import logger_handler
from app_commands.termcolors import OutputWrapper


class AppCommands:
    def __init__(
        self,
        app=None,
        entrypoint=None,
        commands_module=None,
        exception_handler=None,
        stdout=None,
        stderr=None,
    ):
        self.app = app
        self.entrypoint = entrypoint or find_entrypoint()
        self.module = load_commands_module(
            commands_module or f'{self.entrypoint}.commands'
        )
        self.exception_handler = exception_handler or logger_handler
        self.stdout = OutputWrapper(stdout or sys.stdout)
        self.stderr = OutputWrapper(stderr or sys.stderr)
        self.cli_group = self.create_cli_group()
        self.load_commands()

    def run(self, argv=None):
        argv = argv or sys.argv
        prog_name = f'python -m {self.entrypoint}'
        self.cli_group.main(argv[1:], prog_name)

    def load_commands(self):
        for _, slug, _ in pkgutil.iter_modules(self.module.__path__):
            module_name = f'{self.module.__package__}.{slug}'
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue
            command = getattr(module, 'Command', None)
            if isinstance(command, type) and issubclass(command, BaseCommand):
                command.command_name = slug
                self.add_cli_command(slug, command)

    def create_cli_group(self):
        options = [
            click.Option(
                ['--healthcheck'],
                type=int,
                metavar='PORT',
                help='Enable health check server on port',
            ),
            click.Option(
                ['--lifespan/--no-lifespan'],
                help='Enable/disable app lifespan',
                default=None,
            ),
        ]
        return click.Group('cli', params=options)

    def add_cli_command(self, command_name, command):
        help_text = command.help
        if help_text is None:
            help_text = inspect.getdoc(command.handle)
            if isinstance(help_text, bytes):
                help_text = help_text.decode('utf-8')
        else:
            help_text = inspect.cleandoc(help_text)
        self.cli_group.add_command(
            click.Command(
                name=command_name,
                callback=partial(self.run_command, command),
                params=command.get_click_parameters(),
                help=help_text,
                context_settings={
                    'allow_extra_args': command.allow_extra_args,
                },
            )
        )

    def run_command(self, command, *args, **kwargs):
        options = {
            'app': self.app,
            'stdout': self.stdout,
            'stderr': self.stderr,
        }

        context = click.get_current_context()
        if context.parent:
            options.update(context.parent.params)

        async def run_command_instance():
            instance = command(**options)
            with self.exception_handler(instance):
                await instance.run(*args, **kwargs)

        try:
            asyncio.run(run_command_instance())
        except (KeyboardInterrupt, SystemExit):
            pass


def find_entrypoint():
    frame = inspect.stack()[2]
    module = inspect.getmodule(frame[0])
    if module.__name__ != '__main__':
        raise RuntimeError(
            'AppCommand should only be instantiated from a __main__ module.'
        )
    return module.__package__


def load_commands_module(name):
    try:
        return importlib.import_module(name)
    except ImportError:
        raise RuntimeError(
            f'Could not load module "{name}". You must set commands_module '
            f'on AppCommand to a valid python module.'
        )
