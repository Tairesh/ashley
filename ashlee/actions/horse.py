import os
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action
from ashlee.utils import random_file


class Horse(Action):

    DIR = os.path.join(os.getcwd(), 'res', 'horse')

    def get_description(self) -> str:
        return "случайная лошадь"

    def get_keywords(self) -> List[str]:
        return ['скинь лошадь', 'покажи лошадь', 'скинь коня', 'покажи коня',
                'скинь лошадку', 'покажи лошадку']

    def get_cmds(self) -> List[str]:
        return ['horse']

    def get_name(self) -> str:
        return emoji.HORSE + " Лошадь"

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        self.bot.send_photo(message.chat.id, open(random_file(self.DIR), 'rb'), reply_to_message_id=message.message_id)
