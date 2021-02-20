from typing import List
import random
import urllib.request
from urllib.parse import quote
from xml.etree import ElementTree

from telebot.types import Message

from ashlee import emoji, utils, stickers, funny
from ashlee.action import Action


class Anime(Action):

    API_URL = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags={}"

    def get_description(self) -> str:
        return 'случайная картинка с gelbooru.com по тегу'

    def get_keywords(self) -> List[str]:
        return ['аниме']

    def get_cmds(self) -> List[str]:
        return ['anime', 'a']

    def get_name(self) -> str:
        return emoji.SEARCH + " Anime"

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        if message.text.startswith('/'):
            keyword = utils.get_keyword(message)
            if not keyword:
                cmd = utils.get_command(message)
                req = random.choice(funny.ANIME_REQUESTS)
                self.bot.reply_to(message, f"Пример использования команды:\n`/{cmd} {req}`",
                                  parse_mode='Markdown')
                return
        else:
            if message.reply_to_message and message.reply_to_message.text:
                keyword = message.reply_to_message.text
            else:
                keyword = 'sfw'

        request_url = self.API_URL.format(quote(keyword))
        root = ElementTree.parse(urllib.request.urlopen(request_url)).getroot()
        posts = root.findall('post')
        random.shuffle(posts)
        for post in posts:
            url = post.attrib['file_url']
            ext = url.split('.').pop()
            if ext in {'jpg', 'jpeg', 'png'}:
                self.bot.send_photo(message.chat.id, url, None, message.message_id)
                return
            elif ext == 'mp4':
                self.bot.send_video(message.chat.id, url, None, None, message.message_id)
                return

        self.bot.send_sticker(message.chat.id, stickers.FOUND_NOTHING, message.message_id)
