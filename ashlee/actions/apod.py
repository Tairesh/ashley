import json
from typing import List

import requests
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Apod(Action):

    API_URL = "https://api.nasa.gov/planetary/apod?api_key=%APIKEY%"

    def get_description(self) -> str:
        return "Astronomy Picture of the Day"

    def get_keywords(self) -> List[str]:
        return []

    def get_cmds(self) -> List[str]:
        return ['apod']

    def get_name(self) -> str:
        return emoji.SPACE + " APOD"

    def after_loaded(self):
        self.API_URL = self.API_URL.replace('%APIKEY%', self.tgb.api_keys['nasa_apikey'])

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        data = json.loads(requests.get(self.API_URL).content.decode('utf-8'))
        self.bot.send_photo(message.chat.id, data['hdurl'], data['explanation'], reply_to_message_id=message.message_id)
