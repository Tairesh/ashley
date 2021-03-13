import os
from typing import List

from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action
from ashlee.utils import random_file


class Frog(Action):

    DIR = os.path.join(os.getcwd(), 'res', 'frog')

    def get_description(self) -> str:
        return "случайная легущка"

    def get_keywords(self) -> List[str]:
        return ['скинь лягушку', 'покажи лягушку', 'скинь легушку', 'покажи легушку',
                'скинь лягущку', 'покажи лягущку', 'скинь лягущку', 'покажи лягущку',
                'скинь жабу', 'покажи жабу']

    def get_cmds(self) -> List[str]:
        return ['frog', 'toad']

    def get_name(self) -> str:
        return emoji.FROG + " Лягушка"

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        self.bot.send_photo(message.chat.id, open(random_file(self.DIR), 'rb'), reply_to_message_id=message.message_id)
