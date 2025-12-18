import logging
from pathlib import Path
import uuid
import threading

from bot.logging_config import setup_logging
from telebot import TeleBot

from bot.constants import FOLDER_NAME

setup_logging()


class FileStealer:

    def __init__(
        self,
        token: str,
        chat_id: str,
        folder_name: str = FOLDER_NAME
    ):
        self.chat_id = chat_id
        self.bot = TeleBot(token)
        self.folder_name = folder_name

        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(content_types=['document'])
        def handle_doc(message):
            print('Хендлер сработал')
            # if message.chat.id != self.chat_id:
            #     print('Хуевый id')
            #     return
            file_info = self.bot.get_file(message.document.file_id)
            print('Файл получен')
            data = self.bot.download_file(file_info.file_path)
            print('Файл скачан')
            filename = message.document.file_name
            folder_path = self._make_dir(self.folder_name)
            with open(folder_path / filename, 'wb') as file:
                file.write(data)

            print(f'файл сохранен: {filename}')

    def _make_dir(self, folder_name: str) -> Path:
        """Защищенный метод, создает директорию."""
        try:
            file_path = Path(__file__).parent.parent / folder_name
            logging.debug('Путь к файлу: %s', file_path)
            file_path.mkdir(parents=True, exist_ok=True)
            return file_path
        except Exception as error:
            logging.error('Не удалось создать директорию по причине %s', error)
            raise

    def run(self, lifetime_seconds: int):
        def shutdown():
            print('Время жизни истекло, останавливаем бота')
            self.bot.stop_polling()
        threading.Timer(lifetime_seconds, shutdown).start()
        print(f'Бот запущен, время жизни = {lifetime_seconds} сек')
        self.bot.polling(none_stop=True)
        # self.bot.polling(timeout=60)
        print('Бот завершил работу')
