from typing import List
import random
import urllib.request
from urllib.parse import quote
from xml.etree import ElementTree

from telebot.apihelper import ApiException
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

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

    def get_callback_start(self):
        return 'anime:'

    def after_loaded(self):
        if self.tgb.debug:
            self.API_URL = "http://localhost/gelbooru.xml"

    @Action.send_uploading_photo
    def _try_send_photo(self, message) -> bool:
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

    def btn_pressed(self, call: CallbackQuery):
        if call.data.endswith('sudo'):
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(f"{emoji.CHECK} Да", callback_data='anime:yes'),
                InlineKeyboardButton(f"{emoji.CANCEL} Отмена", callback_data='anime:cancel'),
            ]])
            self.bot.edit_message_text(
                f"{call.message.text}\nВы действительно хотите потратить {emoji.LEMON} и отправить аниме?",
                call.message.chat.id, call.message.message_id, reply_markup=kb
            )
            return
        elif call.data.endswith('cancel'):
            self.bot.edit_message_text(f"{emoji.ERROR} Аниме запрещено в этом чате!",
                                       call.message.chat.id, call.message.message_id, reply_markup=None)
            return
        elif call.data.endswith('yes'):
            if not call.message.reply_to_message:
                return
            user = self.db.get_user(call.message.reply_to_message.from_user.id)
            if user.lemons > 0:
                self.bot.edit_message_text(f"{emoji.ERROR} Аниме запрещено в этом чате!\n"
                                           f"Но тем у кого много лимонов закон не писан...",
                                           call.message.chat.id, call.message.message_id, reply_markup=None)
                if self._try_send_photo(call.message.reply_to_message):
                    self.db.update_user_lemons(user.id, user.lemons - 1)
            else:
                self.bot.edit_message_text(f"{emoji.ERROR} Аниме запрещено в этом чате!",
                                           call.message.chat.id, call.message.message_id, reply_markup=None)

    @Action.save_data
    def call(self, message: Message):
        settings = self.db.get_chat_settings(message.chat.id)
        if settings and not settings.enabled_anime:
            user = self.db.get_user(message.from_user.id)
            if user.lemons > 0:
                kb = InlineKeyboardMarkup([[
                    InlineKeyboardButton(f"{emoji.LEMON} Потратить лимон и всё равно отправить",
                                         callback_data='anime:sudo')
                ]])
            else:
                kb = None
            self.bot.reply_to(message, f"{emoji.ERROR} Аниме запрещено в этом чате!", reply_markup=kb)
            return

        self._try_send_photo(message)
