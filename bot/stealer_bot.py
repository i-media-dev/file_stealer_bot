import logging
import random
import threading
from pathlib import Path

import pandas as pd
from telebot import TeleBot

from bot.constants import FOLDER_NAME, ROBOTS
from bot.logging_config import setup_logging

setup_logging()


class FileStealer:

    def __init__(
        self,
        token: str,
        chat_id: int,
        folder_name: str = FOLDER_NAME
    ):
        self.chat_id = chat_id
        self.bot = TeleBot(token)
        self.folder_name = folder_name

        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(content_types=['document'])
        def handle_doc(message):
            # if message.chat.id != self.chat_id:
            #     print('Хуевый id')
            #     return
            file_info = self.bot.get_file(message.document.file_id)
            data = self.bot.download_file(file_info.file_path)
            filename = message.document.file_name
            logging.info('Файл %s скачан', filename)
            folder_path = self._make_dir(self.folder_name)
            file_path = folder_path / filename
            with open(file_path, 'wb') as file:
                file.write(data)
            df = pd.read_csv(file_path, delimiter=',', encoding='windows-1251')
            df.to_csv(
                file_path,
                sep=';',
                index=False,
                encoding='utf-8',
            )
            logging.info('файл сохранен: %s', filename)
            random_robot = random.choice(ROBOTS)
            self._get_robot(random_robot, self.chat_id)

    def _get_robot(self, robot, chat_id, robot_folder='robot'):
        try:
            with open(f'{robot_folder}/{robot}', 'rb') as photo:
                self.bot.send_sticker(chat_id, photo)
        except FileNotFoundError:
            logging.warning('Робот %s не найден', robot)

    def _make_dir(self, folder_name: str) -> Path:
        """Защищенный метод, создает директорию."""
        try:
            file_path = Path(__file__).parent.parent / folder_name
            file_path.mkdir(parents=True, exist_ok=True)
            logging.debug('Путь к файлу - %s', file_path)
            return file_path
        except Exception as error:
            logging.error('Не удалось создать директорию по причине %s', error)
            raise

    def run(self, lifetime_seconds: int):
        def shutdown():
            self.bot.stop_polling()
        threading.Timer(lifetime_seconds, shutdown).start()
        logging.info('Бот запущен, время жизни = %s сек', lifetime_seconds)
        # self.bot.polling(none_stop=True)
        self.bot.polling(timeout=60)
