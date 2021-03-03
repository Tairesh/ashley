import os
import re
from hashlib import md5
from typing import Union

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

    return name.strip()


def escape(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
