import json
from typing import List

import requests
from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action
from ashlee.constants import ADMINS


class InvalidResult(Exception):
    pass


class Gpt(Action):

    API_URL = "https://api.aicloud.sbercloud.ru/public/v1/public_inference/gpt3/predict"
    queue = []

    def get_description(self) -> str:
        return "сгенерировать МНОГО бреда"

    def get_keywords(self) -> List[str]:
        return []

    def get_cmds(self) -> List[str]:
        return ['gpt3', ]

    def get_name(self) -> str:
        return emoji.DICE + " GPT3"

    def _done(self):
        Gpt.queue.pop(0)
        if len(Gpt.queue) > 0:
            self._do_request(Gpt.queue[0])

    @Action.send_typing
    def _do_request(self, message: Message):
        text = utils.get_keyword(message)
        if not text:
            self.bot.reply_to(message, f"{emoji.INFO} Необходимо указать «затравку» для генерации текста!")
            self._done()
            return

        error_message = None
        for tries in range(10):
            try:
                data = json.loads(requests.post(self.API_URL, json={'text': text}, timeout=5).content.decode('utf-8'))
                result = data['predictions'].strip()
                if not result or result == text:
                    raise InvalidResult()
                self.bot.reply_to(message, result)
                if error_message:
                    self.bot.delete_message(message.chat.id, error_message.message_id)
                self._done()
                return
            except (json.JSONDecodeError, requests.exceptions.ReadTimeout, InvalidResult):
                if error_message is None:
                    error_message = self.bot.reply_to(message,
                                                      f"{emoji.ERROR} API ruGPT3 временно недоступно! Попробую снова...")
                elif message.from_user.id in ADMINS:
                    self.bot.edit_message_text(
                        chat_id=message.chat.id, message_id=error_message.message_id,
                        text=f"{emoji.ERROR} API ruGPT3 временно недоступно! Попробую снова (x{tries+1})..."
                    )
        self._done()

    @Action.save_data
    def call(self, message: Message):
        Gpt.queue.append(message)
        if len(Gpt.queue) == 1:
            self._do_request(Gpt.queue[0])
        else:
            self.bot.reply_to(message, f"{emoji.INFO} Запрос добавлен в очередь, заявки перед вами: {len(Gpt.queue)-1}")
