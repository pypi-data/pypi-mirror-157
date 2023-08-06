import asyncio

from app_commands.base import BaseCommand


class Command(BaseCommand):
    healthcheck_port = 8000
    help = 'Test healthcheck server'

    async def handle(self, *args, **kwargs):
        self.stdout.write(f'Health check on port {self.healthcheck_port}')
        await asyncio.sleep(30)

    async def get_healthchecks(self):
        return {
            'db': self.check_db,
            'cache': self.check_cache,
        }

    async def check_db(self):
        await asyncio.sleep(0.3)
        return True

    async def check_cache(self):
        await asyncio.sleep(0.1)
        return True
