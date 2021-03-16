import json
from typing import List
import random
from urllib.parse import quote

import requests
from telebot.apihelper import ApiException
from telebot.types import Message

from ashlee import emoji, utils, stickers, constants
from ashlee.action import Action


class Gimage(Action):

    API_URL = "https://www.googleapis.com/customsearch/v1" \
              "?q={}&start=1&key=%KEY%&cx=%CX%&searchType=image&gl=ru&imgSize=xxlarge"
    FUNNY_EXAMPLES = [
        'child porn',
        'перламутровый',
        'joseph stalin rule 34',
        'big floppa',
        'не чёрные предметы не являющиеся воронами',
    ]

    def get_description(self) -> str:
        return "поиск картинок в гугле"

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
        chat = self.db.get_chat(message.chat.id)
        vip_chat = False
        for admin in constants.ADMINS:
            if admin in chat.users:
                vip_chat = True
                break
        if not vip_chat:
            self.bot.reply_to(message, "Эта команда работает только в моих любимых чатах!")
            return

        if message.text.startswith('/'):
            keyword = utils.get_keyword(message)
            if not keyword:
                cmd = utils.get_command(message)
                req = random.choice(self.FUNNY_EXAMPLES)
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
                if not url.startswith('http'):
                    continue
                try:
                    self.bot.send_photo(message.chat.id, url, None, message.message_id)
                    return
                except ApiException:
                    pass

        self.bot.send_sticker(message.chat.id, stickers.FOUND_NOTHING, message.message_id)
