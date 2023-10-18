import json
from typing import List

import requests
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Dog(Action):

    API_URL = "https://dog.ceo/api/breeds/image/random"
    WHIPPET_URL = "https://dog.ceo/api/breed/whippet/images/random"

    def get_description(self) -> str:
        return "случайное фото собаки"

    def get_keywords(self) -> List[str]:
        return ["скинь собаку", "покажи собаку"]

    def get_cmds(self) -> List[str]:
        return ["dog", "viktor"]

    def get_name(self) -> str:
        return emoji.DOG + " Dogs"

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        api_url = self.API_URL
        if message.text.startswith("/viktor"):
            api_url = self.WHIPPET_URL
        data = json.loads(requests.get(api_url).content.decode("utf-8"))
        url = data["message"]
        if url.endswith(".gif"):
            self.bot.send_video(
                message.chat.id, url, reply_to_message_id=message.message_id
            )
        else:
            self.bot.send_photo(
                message.chat.id, url, reply_to_message_id=message.message_id
            )
