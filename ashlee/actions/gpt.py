import json
from typing import List

import requests
from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Gpt(Action):

    API_URL = "https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict"

    def get_description(self) -> str:
        return "сгенерировать МНОГО бреда"

    def get_keywords(self) -> List[str]:
        return []

    def get_cmds(self) -> List[str]:
        return ['gpt3', ]

    def get_name(self) -> str:
        return emoji.DICE + " GPT3"

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        text = utils.get_keyword(message)
        data = json.loads(requests.post(self.API_URL, json={'text': text}).content.decode('utf-8'))
        self.bot.reply_to(message, data['predictions'])
