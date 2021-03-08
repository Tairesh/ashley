from typing import List
import random
import urllib.request
from urllib.parse import quote
from xml.etree import ElementTree

from telebot.apihelper import ApiException

from ashlee import emoji, utils, stickers, funny
from ashlee.action import SudoAction


class Anime(SudoAction):

    API_URL = "https://gelbooru.com/index.php?page=dapi&s=post&q=index&tags={}"

    def _get_label(self) -> str:
        return 'Аниме'

    def _get_settings_attr(self) -> str:
        return 'enabled_anime'

    def get_description(self) -> str:
        return 'случайная картинка с gelbooru.com по тегу'

    def get_keywords(self) -> List[str]:
        return ['аниме']

    def get_cmds(self) -> List[str]:
        return ['anime', 'a']

    def get_name(self) -> str:
        return emoji.SEARCH + " Аниме"

    def get_callback_start(self):
        return 'anime:'

    def after_loaded(self):
        if self.tgb.debug:
            self.API_URL = "http://localhost/gelbooru.xml"

    @SudoAction.send_uploading_photo
    def _try_process_action(self, message) -> bool:
        if message.text.startswith('/'):
            keyword = utils.get_keyword(message)
            if not keyword:
                cmd = utils.get_command(message)
                req = random.choice(funny.ANIME_REQUESTS)
                self.bot.reply_to(message, f"Пример использования команды:\n`/{cmd} {req}`",
                                  parse_mode='Markdown')
                return False
        else:
            keyword = 'safe'

        request_url = self.API_URL.format(quote(keyword))
        root = ElementTree.parse(urllib.request.urlopen(request_url)).getroot()
        posts = root.findall('post')
        random.shuffle(posts)
        for post in posts:
            url = post.attrib['file_url']
            ext = url.split('.').pop()
            try:
                if ext in {'jpg', 'jpeg', 'png'}:
                    self.bot.send_photo(message.chat.id, url, None, message.message_id)
                    return True
                elif ext == 'mp4':
                    self.bot.send_video(message.chat.id, url, None, None, message.message_id)
                    return True
            except ApiException:
                continue

        self.bot.send_sticker(message.chat.id, stickers.FOUND_NOTHING, message.message_id)
        return False
