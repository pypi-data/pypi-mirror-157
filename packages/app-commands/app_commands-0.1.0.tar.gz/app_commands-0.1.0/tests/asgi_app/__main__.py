from app_commands.commands import AppCommands
from tests.asgi_app import app

if __name__ == '__main__':
    AppCommands(app).run()
