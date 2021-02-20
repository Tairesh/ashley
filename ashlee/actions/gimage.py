import json
from typing import List
import random
from urllib.parse import quote

import requests
from telebot.types import Message

from ashlee import emoji, utils, stickers, funny
from ashlee.action import Action


class Gimage(Action):

    API_URL = "https://www.googleapis.com/customsearch/v1" \
              "?q={}&start=1&key=%KEY%&cx=%CX%&searchType=image&gl=ru&imgSize=xxlarge"

    def get_keywords(self) -> List[str]:
        return ['найди картинку', 'гугл картинки']

    def get_cmds(self) -> List[str]:
        return ['gimage', 'gi', 'pic']

    def get_name(self) -> str:
        return emoji.SEARCH + " Pictures"

    def after_loaded(self):
        Gimage.API_URL = Gimage.API_URL.replace('%KEY%', self.tgb.api_keys['google_apikey'])
        Gimage.API_URL = Gimage.API_URL.replace('%CX%', self.tgb.api_keys['google_cx'])

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        if message.text.startswith('/'):
            keyword = utils.get_keyword(message)
            if not keyword:
                cmd = utils.get_command(message)
                req = random.choice(funny.IMAGE_REQUESTS)
                self.bot.reply_to(message, f"Пример использования команды:\n`/{cmd} {req}`",
                                  parse_mode='Markdown')
                return
        else:
            if message.reply_to_message and message.reply_to_message.text:
                keyword = message.reply_to_message.text
            else:
                self.bot.reply_to(message, "Эту команду пока можно использовать только в ответ на другое сообщение.")
                return

        data = json.loads(requests.get(self.API_URL.format(quote(keyword))).content.decode('utf-8'))
        if 'items' in data:
            for row in data['items']:
                url = row['link']
                self.bot.send_photo(message.chat.id, url, None, message.message_id)
                return

        self.bot.send_sticker(message.chat.id, stickers.FOUND_NOTHING, message.message_id)
