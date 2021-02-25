import random
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Dicks(Action):

    IMAGE_URL = "https://thisdickpicdoesnotexist.com/stylegan2_fakes/{}.jpg"
    MIN_ID = 1000
    MAX_ID = 9193

    def get_description(self) -> str:
        return "нейросетевой дикпик"

    def get_keywords(self) -> List[str]:
        return ['сгенерируй хуй']

    def get_cmds(self) -> List[str]:
        return ['dicks']

    def get_name(self) -> str:
        return emoji.STRAWBERRY + " Dicks"

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        settings = self.db.get_chat_settings(message.chat.id)
        if settings and not settings.enabled_porn:
            self.bot.reply_to(message, f"{emoji.ERROR} Порно запрещено в этом чате!")
            return

        img_id = random.randint(self.MIN_ID, self.MAX_ID)
        self.bot.send_photo(message.chat.id, self.IMAGE_URL.format(img_id), None, message.message_id)
