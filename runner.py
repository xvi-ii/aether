import os
import aether
import dotenv
import logging
import logging.config
import trio

log = logging.basicConfig(level=logging.DEBUG)
dotenv.load_dotenv()

async def run(token):
    async with aether.Connection(token=token) as gw:
        ...

if __name__ == '__main__':
    trio.run(run, os.getenv("BOT_TOKEN"))