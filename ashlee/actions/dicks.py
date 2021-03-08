import random
from typing import List

from telebot.apihelper import ApiException
from telebot.types import Message

from ashlee import emoji
from ashlee.action import SudoAction


class Dicks(SudoAction):

    IMAGE_URL = "https://thisdickpicdoesnotexist.com/stylegan2_fakes/{}.jpg"
    MIN_ID = 1000
    MAX_ID = 9193

    def _get_label(self) -> str:
        return 'Порно'

    def _get_settings_attr(self) -> str:
        return 'enabled_porn'

    @SudoAction.send_uploading_photo
    def _try_process_action(self, message: Message) -> bool:
        img_id = random.randint(self.MIN_ID, self.MAX_ID)
        try:
            self.bot.send_photo(message.chat.id, self.IMAGE_URL.format(img_id), None, message.message_id)
            return True
        except ApiException:
            return False

    def get_description(self) -> str:
        return "нейросетевой дикпик"

    def get_keywords(self) -> List[str]:
        return ['сгенерируй хуй']

    def get_cmds(self) -> List[str]:
        return ['dicks']

    def get_name(self) -> str:
        return emoji.STRAWBERRY + " Dicks"

    def get_callback_start(self) -> str:
        return 'dicks:'
