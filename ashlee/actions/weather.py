import json
from typing import List
from urllib.parse import quote
from datetime import datetime, timezone, timedelta

import requests
from telebot.types import Message

from ashlee import emoji, utils, stickers
from ashlee.action import Action


class Weather(Action):
    OPENWEATHERMAP_API = "https://api.openweathermap.org/data/2.5/weather?q={}&appid=%APPID%&lang=ru&units=metric"

    def get_description(self) -> str:
        return 'узнать погоду'

    def get_name(self) -> str:
        return emoji.WEATHER + ' Погода'

    def get_cmds(self) -> List[str]:
        return ['weather']

    def get_keywords(self) -> List[str]:
        return []

    def after_loaded(self):
        Weather.OPENWEATHERMAP_API = Weather.OPENWEATHERMAP_API.replace('%APPID%',
                                                                        self.tgb.api_keys['openweathermap_appid'])

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.text.startswith('/'):
            if message.reply_to_message:
                text = message.reply_to_message.text
            else:
                text = utils.get_keyword(message)
        else:
            text = message.text
        if not text:
            self.bot.reply_to(message, "Пример использования команды:\n`/weather New York`", parse_mode="Markdown")
            return

        data = json.loads(requests.get(self.OPENWEATHERMAP_API.format(quote(text))).content.decode('utf-8'))
        if 'cod' in data and data['cod'] == 200:
            tz = timezone(timedelta(seconds=data['timezone']))
            result = f"<b>{data['name']}</b>\nПогода: {', '.join([w['description'] for w in data['weather']])}\n"
            result += "Температура: "
            temp_min = round(data['main']['temp_min'])
            temp_max = round(data['main']['temp_max'])
            if temp_max != temp_min:
                result += f"от {temp_min}C° до {temp_max}C°"
            else:
                result += f"{temp_min}C°"
            result += f", ощущается как {round(data['main']['feels_like'])}C°\n"
            result += f"Ветер: {data['wind']['deg']}°, {data['wind']['speed']} м/с"
            if 'gust' in data['wind']:
                result += f", порывы до {data['wind']['gust']} м/с"
            result += '\n'
            result += f"Рассвет: {datetime.fromtimestamp(data['sys']['sunrise'], tz).strftime('%H:%M')}"
            result += f", закат: {datetime.fromtimestamp(data['sys']['sunset'], tz).strftime('%H:%M')}\n"
            result += f"Давление: {data['main']['pressure']} гПа\n"
            result += f"Облачность: {data['clouds']['all']}%"

            self.bot.reply_to(message, result, parse_mode="HTML")
        elif 'cod' in data and int(data['cod']) == 404:
            self.bot.reply_to(message, f"{emoji.SAD} Не могу найти такое место «{text}»")
        else:
            self.bot.send_sticker(message.chat.id, stickers.SOMETHING_WRONG, message.message_id)
