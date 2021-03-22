import datetime
import os
import random
import re
import urllib.error
from hashlib import md5
from typing import Union

import feedparser
import requests
from telebot.types import Message, User, Chat

from ashlee.database import User as DBUser

r_ashley = re.compile(r'([^\w]|^)(эшли|эщли|ashley|ashlee|ashlea|ashli|єшли|ешлі|єшлі)', flags=re.IGNORECASE)


def get_command(message: Message):
    return message.text.split(' ')[0].split('@')[0][1:].lower()


def get_atmention(message: Message):
    if '@' in message.text:
        command = message.text.split(' ')[0].split('@')
        return command[1] if len(command) > 1 else None
    return None


def get_keyword(message: Message, with_reply=True) -> str:
    keyword = message.text[len(message.text.split(' ')[0]) + 1::].replace(',', '').strip()
    if with_reply and not keyword and message.reply_to_message:
        rm = message.reply_to_message
        keyword = rm.caption if rm.caption else rm.text
    return keyword


def is_for_me(message: Message, me: User):
    chat: Chat = message.chat
    if chat.type == 'private':
        return True
    if message.reply_to_message and message.reply_to_message.from_user.id == me.id and message.reply_to_message.text:
        return True
    if r_ashley.search(message.text):
        return True

    return False


def chunks(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start + n]


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def download_file(url: str) -> str:
    file_name = os.path.join('downloads', md5(url.encode()).hexdigest())
    r = requests.get(url, timeout=2)
    with open(file_name, 'wb') as f:
        f.write(r.content)
    return file_name


def user_name(user: Union[User, DBUser], with_username=False, prefer_username=False):
    if prefer_username and user.username:
        return '@' + user.username

    name = user.first_name
    if with_username and user.username:
        name += ' @' + user.username
    if user.last_name:
        name += ' ' + user.last_name

    name = name.replace('ᅠ', '')
    return name.strip()


def escape(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')


def format_number(n: int, s0: str, s1: str, s2: str) -> str:
    result = str(n) + ' '
    if n == 0:
        result += s0
    elif n == 1 or (n % 10 == 1 and n != 11 and n % 100 != 11):
        result += s1
    elif n > 100 and 12 <= n % 100 <= 14:
        result += s0
    elif (2 <= n % 10 <= 4 and n > 20) or (2 <= n <= 4):
        result += s2
    else:
        result += s0
    return result


def human_delta_t(dt: datetime.timedelta):
    if dt.total_seconds() <= 0:
        if dt.total_seconds() > -60:
            return 'только что'
        elif dt.total_seconds() > -60*10:
            return 'недавно'
        else:
            return 'давно'
    else:
        hours = dt.seconds // (60*60)
        minutes = (dt.seconds - (hours * 60 * 60)) // 60
        seconds = dt.seconds - (hours * 60 * 60) - (minutes * 60)
        if dt.days > 0:
            return f"через: {format_number(dt.days, 'дней', 'день', 'дня')} " \
                   f"{format_number(hours, 'часов', 'час', 'часа')} " \
                   f"{format_number(minutes, 'минут', 'минута', 'минуты')} " \
                   f"{format_number(seconds, 'секунд', 'секунда', 'секунды')}"
        elif dt.seconds > 60*60:
            return f"через: {format_number(hours, 'часов', 'час', 'часа')} " \
                   f"{format_number(minutes, 'минут', 'минута', 'минуты')} " \
                   f"{format_number(seconds, 'секунд', 'секунда', 'секунды')}"
        elif dt.seconds > 60:
            return f"через: {format_number(minutes, 'минут', 'минута', 'минуты')} " \
                   f"{format_number(seconds, 'секунд', 'секунда', 'секунды')}"
        else:
            return f"через: {format_number(seconds, 'секунд', 'секунда', 'секунды')}"


def random_file(files_dir):
    files = [os.path.join(files_dir, f) for f in os.listdir(files_dir)
             if os.path.isfile(os.path.join(files_dir, f)) and not f.startswith('.')]
    return random.choice(files)


def unique(ar: list) -> list:
    return list(set(ar))


def feed_parse(url):
    try:
        return feedparser.parse(url)
    except urllib.error.URLError:
        return None
