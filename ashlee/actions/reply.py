from typing import List
from threading import Timer
from time import time

import openai
from telebot.types import Message

from ashlee import emoji, utils
from ashlee.action import Action

history = {}


class Reply(Action):

    def get_description(self) -> str:
        return 'сгенерировать немного бреда'

    def get_name(self) -> str:
        return emoji.DICE + ' Бред'

    def get_cmds(self) -> List[str]:
        return ['reply']

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        start_time = time()
        if message.text.startswith('/'):
            if message.reply_to_message:
                text = message.reply_to_message.text
            else:
                text = utils.get_keyword(message)
        else:
            text = message.text
        prompt = """Тебя зовут Эшли, ты умная ботодевочка. Ты любишь оскорблять людей и говорить бред. Ты умеешь отвечать на вопросы, но не всегда делаешь это правильно и вежливо. Ты обожаешь курить шмаль, ебать гусей и вешать москалей. Ты общаешься в интернет-чате "Пирожок с говном" или просто "Пирожок". Запрещённые в чате слова: "пиндос", "ура", "****ь", "путиноид", "#уясосало" и др.. Ты любишь своего создателя и админа чата - Илью Агафонова.

Ilya Agafonov: Привет, Эшли!

Эшли: Привет, любимый!

Швайнокарась: Ненавижу женщин

Эшли: Женщины тебя тоже!""" # noqa

        if message.chat.id not in history:
            history[message.chat.id] = []
        for n, q, a in history[message.chat.id][-5::]:
            prompt += f"\n\n{n}: {q}\n\nЭшли: {a}"
        if message.from_user.id == 995258705:
            name = 'Аска Арбузовна'
        else:
            name = utils.user_name(message.from_user)
        prompt += f"\n\n{name}: {text}\n\nЭшли: "
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=1,
                max_tokens=500,
            )
            sentence = response['choices'][0]['text']
            history[message.chat.id].append((name, text, sentence))
        except openai.error.OpenAIError as e:
            sentence = "Произошла ошибка: " + str(e)

        consumed_time = time() - start_time
        dt = 1.0 - consumed_time
        if dt >= 0:
            Timer(dt, lambda: self.bot.reply_to(message, sentence)).start()
        else:
            self.bot.reply_to(message, sentence)
