import json
import asyncio
import pyrogram
from handler import handler


class Bot:
    def __init__(self, config_file):
        # check config file exists
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f'Config file {config_file} not found')

        self.client = pyrogram.Client(
            self.config['session_name'],
            self.config['api_id'],
            self.config['api_hash']
        )

    def handle_message(self):
        @self.client.on_message()
        async def my_handler(client, message):
            await handler(client, message)

    def __del__(self):
        self.client.stop()


def background():
    bot = Bot('config.json')
    bot.handle_message()
    bot.client.run()


if __name__ == '__main__':
    background()
