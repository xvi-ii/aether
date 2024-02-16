import os
import dotenv
import logging
import logging.config
import trio

from aether.core import Connection

log = logging.basicConfig(level=logging.DEBUG)
dotenv.load_dotenv()

app = Connection()

if __name__ == '__main__':
    trio.run(app.start, os.getenv("BOT_TOKEN"))