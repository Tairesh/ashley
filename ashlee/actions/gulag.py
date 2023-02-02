import json
from typing import List
from urllib.request import url2pathname

import requests
from bs4 import BeautifulSoup
from telebot.types import Message

from ashlee import emoji
from ashlee.action import Action


class Gulag(Action):
    OPENLIST_API = "https://ru.openlist.wiki//api.php?action=OlRandomPage&format=json"
    OPENLIST_URL_PREFIX = "https://ru.openlist.wiki/"

    def get_description(self) -> str:
        return "случайный репрессированный"

    def get_name(self) -> str:
        return emoji.ERROR + " Гулаг"

    def get_cmds(self) -> List[str]:
        return ["gulag"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        data = json.loads(requests.get(self.OPENLIST_API).content.decode("utf-8"))[
            "OlRandomPage"
        ]
        soup = BeautifulSoup(data["title"] + data["text"]["*"], features="html.parser")

        link = soup.find("a")
        name = link.text
        url = self.OPENLIST_URL_PREFIX + url2pathname(link.attrs["href"])
        short_info = "\n".join(
            map(
                lambda row: row[1:] if row.startswith(" ") else "\n" + row,
                filter(
                    lambda row: row and row != " ",
                    soup.find("div", {"id": "custom-person"}).text.split("\n"),
                ),
            )
        )

        text = f'<a href="{url}">{name}</a>\n{short_info}'
        img = soup.find("img", {"class": "thumbimage"})
        if img:
            imgurl = self.OPENLIST_URL_PREFIX + img.attrs["src"]
            text = f'<a href="{imgurl}">#</a> ' + text
        if len(text) > 3000:
            text = text[:3000] + "…"

        self.bot.reply_to(message, text, parse_mode="HTML")
