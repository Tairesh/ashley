import re
from typing import List
from urllib.parse import quote
import urllib.request

from bs4 import BeautifulSoup
from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action


class Fonosemantic(Action):
    FONOSEMANTIC_URL = "https://psi-technology.net/servisfonosemantika.php"
    r_fonetic = re.compile(r"(?:как звучит слово|как по твоему звучит слово|как по твоему звучит|как звучит) ("
                           r"?:\"|“|”|'|‘|’|«|»)*([абвгдеёжзийёклмнопрстуфхцчшщъыьэюя\*]+)(?:\"|“|”|'|‘|’|«|»)*",
                           flags=re.IGNORECASE)
    r_not_cyrilic = re.compile(r'([^А-Яа-яёЁ*\s])', flags=re.IGNORECASE)
    r_glasnye = re.compile(r'([ауеоыяиэё])', flags=re.IGNORECASE)

    def get_description(self) -> str:
        return 'узнать как звучит слово'

    def get_name(self) -> str:
        return emoji.INFO + ' Фоносемантика'

    def get_cmds(self) -> List[str]:
        return ['fs', 'fs_full']

    def get_keywords(self) -> List[str]:
        return ['как звучит ']

    def _uy2oe(self, string: str) -> str:
        string = string.lower()
        if string[-3::] in {'ший', 'чий', 'щий'}:
            return string[:-2:] + 'ее'
        else:
            return string[:-2:] + 'ое'

    def _get_views(self, keyword: str) -> list:
        data = f"slovo={quote(keyword)}&sub=".encode('ascii')
        req = urllib.request.Request(self.FONOSEMANTIC_URL, data,
                                     {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
        with urllib.request.urlopen(req) as response:
            page = response.read()
            soup = BeautifulSoup(page, features="html.parser")
            table = soup.find('table', {'class': 'prais'})
            trs = table.find_all_next('tr')
            views = []
            for tr in trs:
                tds = tr.find_all('td')
                if len(tds):
                    count = float(tds[1].text.replace(',', '.'))
                    dist = abs(count - 3)
                    view = tds[3].text
                    if view != "Не выражен":
                        views.append((dist, view))
            views = list(sorted(views, key=lambda d: d[0], reverse=True))
            return views

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if message.text.startswith('/'):
            keyword = utils.get_keyword(message).lower()
        else:
            try:
                keyword = self.r_fonetic.search(message.text).group(1).lower()
            except re.error:
                keyword = None
        if not keyword:
            self.bot.reply_to(message, f"{emoji.INFO} Укажи слово для оценки!")
            return
        if self.r_not_cyrilic.search(keyword):
            self.bot.reply_to(message, f"{emoji.SAD} Я пока могу только в кириллицу!")
            return
        if '*' not in keyword:
            gl = self.r_glasnye.search(keyword)
            if not gl:
                self.bot.reply_to(message, f"{emoji.SAD} В слове должны быть гласные!")
                return
            pos = gl.span()[1]
            keyword = keyword[:pos:] + '*' + keyword[pos::]
        if ' ' in keyword:
            keyword = keyword.replace(' ', '')
        keyword_label = keyword.replace('*', '')
        views = self._get_views(keyword)

        if message.text.startswith('/fs_full'):
            values = [f"{self._uy2oe(b)} ({a:.2f})" for a, b in views]
            self.bot.reply_to(message, '\n'.join(values))
        else:
            if len(views) > 1:
                val1, val2 = self._uy2oe(views[0][1]), self._uy2oe(views[1][1])
                reply = f"как нечто {val1} и {val2}"
            elif len(views) == 1:
                val = self._uy2oe(views[0][1])
                reply = f"как нечто {val}"
            else:
                reply = "абсолютно нейтрально"
            self.bot.reply_to(message, f"Слово «{keyword_label}» звучит {reply}")
