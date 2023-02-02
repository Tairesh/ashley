import json
import random
from typing import List

import requests
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Pig(Action):

    API_URL = "https://pixabay.com/api/?key=%KEY%&min_width=200&min_height=200&per_page=200&q=pig"

    def get_description(self) -> str:
        return "случайная свинья"

    def get_keywords(self) -> List[str]:
        return ["скинь свинью", "покажи свинью", "скинь хохла", "покажи хохла"]

    def get_cmds(self) -> List[str]:
        return [
            "pig",
        ]

    def get_name(self) -> str:
        return emoji.PIG + " Pig"

    def after_loaded(self):
        self.API_URL = self.API_URL.replace(
            "%KEY%", self.tgb.api_keys["pixabay_apikey"]
        )

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        data = json.loads(requests.get(self.API_URL).content.decode("utf-8"))
        hit = None
        while not hit:
            hit = random.choice(data["hits"])
            if not hit["largeImageURL"].endswith(".jpg"):
                hit = None  # skipping pngs and other formats

        self.bot.send_photo(
            message.chat.id,
            hit["largeImageURL"],
            reply_to_message_id=message.message_id,
        )
