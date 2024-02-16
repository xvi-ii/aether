import os
import dotenv
import logging
import logging.config
import trio

from aether.core import Client

log = logging.basicConfig(level=logging.DEBUG)
dotenv.load_dotenv()

client = Client()

if __name__ == '__main__':
    trio.run(client.start, os.getenv("BOT_TOKEN"))