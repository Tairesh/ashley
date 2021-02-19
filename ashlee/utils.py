import re

from telebot.types import Message, User, Chat


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
