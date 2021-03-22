import os

from telebot import TeleBot

from ashlee import feedparser, emoji, utils
from ashlee.database import Database


def _get_bot_token():
    token_file = os.path.join('config', 'token.txt')
    if os.path.isfile(token_file):
        with open(token_file, 'r') as file:
            return file.read()
    else:
        exit(f"ERROR: No token file found at '{token_file}'")


def subscribes():
    db = Database(os.path.join('database', 'db.sqlite'))
    bot = TeleBot(_get_bot_token())
    for sub in db.get_all_subscribes():
        d = feedparser.parse(sub.url)
        if not d:
            db.delete_subscribe(sub.chat_id, sub.url)
            bot.send_message(sub.chat_id, f"{emoji.CANCEL} Подписка на {sub.url} была отменена!")
            continue

        for entry in d['entries']:
            if entry['id'] == sub.last_post:
                break
            text = entry['summary']
            text = text.replace('\t', '').replace('\n', '')\
                .replace('<br>', '\n').replace('<br />', '\n').replace('<br/>', '\n')
            text = f"<b><a href=\"{entry['link']}\">{utils.escape(entry['title'])}</a></b>\n" + text
            for piece in utils.chunks(text, 3000):
                bot.send_message(sub.chat_id, piece, parse_mode='HTML')
        if len(d['entries']) > 0:
            db.update_subscribe(d['entries'][0]['id'], sub.chat_id, sub.url)


if __name__ == '__main__':
    subscribes()
