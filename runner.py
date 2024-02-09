import os
import aether
import dotenv
import logging
import logging.config
import trio

log = logging.basicConfig(level=logging.DEBUG)
dotenv.load_dotenv()

client = aether.Client()

if __name__ == '__main__':
    trio.run(client.start, os.getenv("BOT_TOKEN"))