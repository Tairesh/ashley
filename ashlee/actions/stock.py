import json
import random
from typing import List
from urllib.parse import quote

import requests
from telebot.apihelper import ApiException
from telebot.types import Message

from ashlee import emoji, utils, stickers
from ashlee.action import Action


class Stock(Action):
    PIXABAI_API = "https://pixabay.com/api/?key=%KEY%&orientation=horizontal&min_width=400&min_height=300&q={}"

    def is_not_flood(self) -> bool:
        return True

    def get_description(self) -> str:
        return "поиск картинок по pixabay"

    def get_name(self) -> str:
        return emoji.SEARCH + " Stock photo"

    def get_cmds(self) -> List[str]:
        return ["stock"]

    def get_keywords(self) -> List[str]:
        return [" сток "]

    def after_loaded(self):
        Stock.PIXABAI_API = Stock.PIXABAI_API.replace(
            "%KEY%", self.tgb.api_keys["pixabay_apikey"]
        )

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        text = message.text
        if message.text.startswith("/"):
            text = utils.get_keyword(message)
        elif " сток " in text:
            text = text.split(" сток ")[1]
        data = json.loads(
            requests.get(self.PIXABAI_API.format(quote(text))).content.decode("utf-8")
        )
        if data["totalHits"] > 0:
            urls = list(map(lambda hit: hit["largeImageURL"], data["hits"]))
            random.shuffle(urls)
            for url in urls:
                try:
                    self.bot.send_photo(
                        message.chat.id, url, reply_to_message_id=message.message_id
                    )
                    return
                except ApiException:
                    pass

        self.bot.send_sticker(
            message.chat.id, stickers.FOUND_NOTHING, message.message_id
        )
