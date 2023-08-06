import inspect
import logging
from contextlib import contextmanager


@contextmanager
def logger_handler(command):
    try:
        yield
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as exc:
        module = inspect.getmodule(command)
        logger = logging.getLogger(module.__name__)
        logger.exception(f'Error while running command: {command.command_name}')
        raise exc from None
