import json
from typing import List

import requests
from telebot.types import Message

from ashlee import emoji
from ashlee.action import SudoAction


class Boobs(SudoAction):

    API_URL = "http://api.oboobs.ru/boobs/1/1/random"
    MEDIA_SERVER = "http://media.oboobs.ru/"

    def is_not_flood(self) -> bool:
        return True

    def _get_label(self) -> str:
        return 'Порно'

    def _get_settings_attr(self) -> str:
        return 'enabled_porn'

    @SudoAction.send_uploading_photo
    def _try_process_action(self, message: Message) -> bool:
        data = json.loads(requests.get(self.API_URL).content.decode('utf-8'))[0]
        url = self.MEDIA_SERVER + data['preview']
        caption = data['model']

        self.bot.send_photo(message.chat.id, url, caption, message.message_id)
        return True

    def get_description(self) -> str:
        return "случайные сиськи с oboobs.ru"

    def get_keywords(self) -> List[str]:
        return ['сиськи']

    def get_cmds(self) -> List[str]:
        return ['boobs']

    def get_name(self) -> str:
        return emoji.STRAWBERRY + " Boobs"

    def get_callback_start(self) -> str:
        return 'boobs:'
