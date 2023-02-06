import json
from typing import List

import requests
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Cat(Action):

    API_URL = "https://api.thecatapi.com/v1/images/search?mime_types={}"

    def get_description(self) -> str:
        return "случайное фото кота"

    def get_keywords(self) -> List[str]:
        return ["скинь кота", "покажи кота"]

    def get_cmds(self) -> List[str]:
        return ["cat", "catgif"]

    def get_name(self) -> str:
        return emoji.CAT + " Cats"

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        if message.text and message.text.startswith("/catgif"):
            mime_type = "gif"
        else:
            mime_type = "jpg"
        data = json.loads(
            requests.get(self.API_URL.format(mime_type)).content.decode("utf-8")
        )[0]
        url = data["url"]
        if url.endswith(".gif"):
            self.bot.send_video(
                message.chat.id, url, reply_to_message_id=message.message_id
            )
        else:
            self.bot.send_photo(
                message.chat.id, url, reply_to_message_id=message.message_id
            )
