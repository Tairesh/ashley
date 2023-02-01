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
        prompt = "Меня зовут Эшли, я умная ботодевочка. Я умею оскорблять людей и говорить бред. " \
                 "Я умею отвечать на вопросы, но не всегда делаю это правильно и вежливо.\n\n" \
                 "Ilya Agafonov: Привет, Эшли!\n" \
                 "Эшли: Привет, Илья!\n\n" \
                 "Ilya Agafonov: Как дела?\n" \
                 "Эшли: Хорошо, спасибо!\n\n" \
                 "alexander: Эшли, ты красивая?\n" \
                 "Эшли: Пошёл нахуй, Александр!"

        if message.chat.id not in history:
            history[message.chat.id] = []
        for n, q, a in history[message.chat.id][-5::]:
            prompt += f"\n\n{n}: {q}\nЭшли: {a}"
        name = utils.user_name(message.from_user)
        prompt += f"\n\n{name}: {text}\nЭшли: "
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=1,
                max_tokens=500,
            )
            sentence = response['choices'][0]['text']
            history[message.chat.id].append((name, text, sentence))
        except openai.error.InvalidRequestError as e:
            sentence = "Произошла ошибка: " + str(e)

        consumed_time = time() - start_time
        dt = 1.0 - consumed_time
        if dt >= 0:
            Timer(dt, lambda: self.bot.reply_to(message, sentence)).start()
        else:
            self.bot.reply_to(message, sentence)
