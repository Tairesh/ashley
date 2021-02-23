import json
from typing import List

import requests
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Boobs(Action):

    API_URL = "http://api.oboobs.ru/boobs/1/1/random"
    MEDIA_SERVER = "http://media.oboobs.ru/"

    def get_description(self) -> str:
        return "случайные сиськи с oboobs.ru"

    def get_keywords(self) -> List[str]:
        return ['сиськи']

    def get_cmds(self) -> List[str]:
        return ['boobs']

    def get_name(self) -> str:
        return emoji.STRAWBERRY + " Boobs"

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        settings = self.db.get_chat_settings(message.chat.id)
        if settings and not settings.enabled_porn:
            self.bot.reply_to(message, f"{emoji.ERROR} Порно запрещено в этом чате!")
            return

        data = json.loads(requests.get(self.API_URL).content.decode('utf-8'))[0]
        url = self.MEDIA_SERVER + data['preview']
        caption = data['model']

        self.bot.send_photo(message.chat.id, url, caption, message.message_id)
