import json
import random
from typing import List

import requests
from telebot.apihelper import ApiException
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Frog(Action):

    API_URL = "https://pixabay.com/api/?key=%KEY%&min_width=200&min_height=200&per_page=200&q={}"

    def get_description(self) -> str:
        return "случайная легущка"

    def get_keywords(self) -> List[str]:
        return ['скинь лягушку', 'покажи лягушку', 'скинь легушку', 'покажи легушку',
                'скинь лягущку', 'покажи лягущку', 'скинь лягущку', 'покажи лягущку',
                'скинь жабу', 'покажи жабу']

    def get_cmds(self) -> List[str]:
        return ['frog', 'toad']

    def get_name(self) -> str:
        return emoji.TOAD + " Лягушка"

    def after_loaded(self):
        self.API_URL = self.API_URL.replace('%KEY%', self.tgb.api_keys['pixabay_apikey'])

    @Action.save_data
    @Action.send_uploading_photo
    def call(self, message: Message):
        if message.text.startswith('/toad'):
            animal = 'toad'
        elif message.text.startswith('/frog'):
            animal = 'frog'
        else:
            animal = random.choice(['frog', 'toad'])
        data = json.loads(requests.get(self.API_URL.format(animal)).content.decode('utf-8'))
        urls = []
        if data['totalHits'] > 0:
            for hit in data['hits']:
                urls.append(hit['largeImageURL'])
        random.shuffle(urls)
        for url in urls:
            try:
                self.bot.send_photo(message.chat.id, url, reply_to_message_id=message.message_id)
                return
            except ApiException:
                continue
