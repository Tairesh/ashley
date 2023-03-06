import os
from typing import List

from telebot.types import Message
import replicate

from ashlee import emoji
from ashlee.action import Action


class What(Action):
    def get_description(self) -> str:
        return "Определить что на фото"

    def get_name(self) -> str:
        return emoji.QUESTION + " Распознавание кзображений"

    def get_cmds(self) -> List[str]:
        return ["what"]

    def get_keywords(self) -> List[str]:
        return []

    @Action.save_data
    @Action.send_typing
    def call(self, message: Message):
        if not message.reply_to_message or not message.reply_to_message.photo:
            self.bot.reply_to(message, "Отправьте эту команду в ответ на изображение")
            return

        try:
            photo = message.reply_to_message.photo.pop()
            file = self.bot.get_file(photo.file_id)
            file_bytes = self.bot.download_file(file.file_path)
            with open("tmpimage", "wb") as f:
                f.write(file_bytes)

            client = replicate.Client(api_token=self.tgb.api_keys["replicate"])
            model = client.models.get("salesforce/blip")
            version = model.versions.get(
                "2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746"
            )
            inputs = {
                # Input image
                "image": open("tmpimage", "rb"),  # file_bytes,
                # Choose a task.
                "task": "image_captioning",
                # Type question for the input image for visual question answering
                # task.
                # 'question': ...,
                # Type caption for the input image for image text matching task.
                # 'caption': ...,
            }
            output = version.predict(**inputs)

            self.bot.reply_to(message, output)
        except Exception as e:
            self.bot.reply_to(message, "Произошла ошибка: " + str(e))

        os.remove("tmpimage")
