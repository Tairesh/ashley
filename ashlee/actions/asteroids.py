import json
from typing import List

import requests
import datetime
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action
from ashlee.utils import human_delta_t


class Asteroids(Action):

    API_URL = "https://api.nasa.gov/neo/rest/v1/feed?start_date={}&end_date={}&api_key=%APIKEY%"

    def get_description(self) -> str:
        return "Ближайшие к Земле астероиды"

    def get_keywords(self) -> List[str]:
        return ['покажи ближайшие астероиды', 'когда конец света']

    def get_cmds(self) -> List[str]:
        return ['asteroids']

    def get_name(self) -> str:
        return emoji.SPACE + " Asteroids"

    def after_loaded(self):
        self.API_URL = self.API_URL.replace('%APIKEY%', self.tgb.api_keys['nasa_apikey'])

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        now = datetime.date.today()
        then = now + datetime.timedelta(hours=24)
        data = json.loads(requests.get(self.API_URL.format(now, then)).content.decode('utf-8'))
        asteroids = []
        for day in data['near_earth_objects']:
            for row in data['near_earth_objects'][day]:
                name = row['name']
                url = row['nasa_jpl_url']
                size_min = row['estimated_diameter']['kilometers']['estimated_diameter_min']
                if size_min < 50:
                    size_min = row['estimated_diameter']['meters']['estimated_diameter_min']
                    size_max = row['estimated_diameter']['meters']['estimated_diameter_max']
                    size_metrics = "метров"
                else:
                    size_max = row['estimated_diameter']['kilometers']['estimated_diameter_max']
                    size_metrics = "километров"
                hazard = row['is_potentially_hazardous_asteroid']
                approach = row['close_approach_data'][0]['epoch_date_close_approach']
                approach_delta = datetime.datetime.fromtimestamp(approach // 1000) - datetime.datetime.now()
                approach_distance = round(float(row['close_approach_data'][0]['miss_distance']['kilometers']))
                approach_velocity = round(float(row['close_approach_data'][0]['relative_velocity']['kilometers_per_second']))
                if approach_delta.total_seconds() > 0 and approach_delta.days < 1:
                    asteroids.append((name, url, size_min, size_max, size_metrics, hazard,
                                      approach_delta, approach_distance, approach_velocity))

        if len(asteroids) == 0:
            self.bot.reply_to(message, f"В ближайшие сутки никаких астероидов рядом с Землёй не пролетит! "
                                       f"Живите пока, людишки {emoji.SARCASM}")
            return

        asteroids.sort(key=lambda r: r[6])
        text = "<b>Астероиды, приближающиеся к Земле:</b>\n\n"
        for row in asteroids:
            name, url, size_min, size_max, size_metrics, \
                hazard, approach_delta, approach_distance, approach_velocity = row
            text += f"{emoji.WARNING if hazard else emoji.SPACE} <b><a href='{url}'>{name}</a></b> " \
                    f"сближение {human_delta_t(approach_delta)}\n"
            text += f"размер: от {round(size_min):,} до {round(size_max):,} {size_metrics}\n"
            approach_distance = f"{approach_distance:,}".replace(',', ' ')
            text += f"пролетит в {approach_distance} километрах "
            text += f"на скорости {approach_velocity} км/с\n\n"

        self.bot.reply_to(message, text, parse_mode='HTML', disable_web_page_preview=True)
