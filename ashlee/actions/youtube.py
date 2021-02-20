import json
from typing import List
import random
from urllib.parse import quote

import requests
from telebot.types import Message

from ashlee import emoji, utils, stickers, funny
from ashlee.action import Action


class Youtube(Action):

    API_URL = "https://www.googleapis.com/youtube/v3/search?q={}&key=%KEY%&cx=%CX%"

    def get_description(self) -> str:
        return "поиск на YouTube"

    def get_keywords(self) -> List[str]:
        return ['найди на ютубе', 'поиск на ютубе']

    def get_cmds(self) -> List[str]:
        return ['youtube', 'y']

    def get_name(self) -> str:
        return emoji.SEARCH + " YouTube"

    def after_loaded(self):
        Youtube.API_URL = Youtube.API_URL.replace('%KEY%', self.tgb.api_keys['google_apikey'])
        Youtube.API_URL = Youtube.API_URL.replace('%CX%', self.tgb.api_keys['google_cx'])

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.text.startswith('/'):
            keyword = utils.get_keyword(message)
            if not keyword:
                cmd = utils.get_command(message)
                req = random.choice(funny.YOUTUBE_REQUESTS)
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
                if row['id']['kind'] == 'youtube#video':
                    url = "https://www.youtube.com/watch?v=" + row['id']['videoId']
                    self.bot.reply_to(message, url)
                    return

        self.bot.send_sticker(message.chat.id, stickers.FOUND_NOTHING, message.message_id)
