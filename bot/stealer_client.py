import asyncio
import logging
import random
import time
from pathlib import Path

import pandas as pd
from telebot import TeleBot
from telethon import TelegramClient, events

from bot.constants import FOLDER_NAME, ROBOTS, SEND_MESSAGE_RETRIES
from bot.logging_config import setup_logging

setup_logging()


class FileStealerClient:

    def __init__(
        self,
        token: str,
        api_id: int,
        api_hash: str,
        group_id: int,
        folder_name: str = FOLDER_NAME,
    ):
        self.bot = TeleBot(token)
        self.group_id = group_id
        self.folder_name = folder_name
        self.client = TelegramClient(
            'sessions/stealer_session',
            api_id,
            api_hash,
        )

        self._setup_handlers()

    def _setup_handlers(self):
        @self.client.on(events.NewMessage(chats=self.group_id))
        async def handle_message(event):
            logging.info('Получено сообщение в чате %s', event.chat_id)
            logging.info('Тип: %s', event.message.media)
            logging.info('От: %s', event.sender_id)
            if event.document:
                sender = await event.get_sender()
                logging.info('Документ от %s', sender.username)
                folder = self._make_dir(self.folder_name)
                filename = event.document.attributes[0].file_name
                file_path = folder / filename
                if file_path.exists():
                    file_path.unlink()
                await event.download_media(file=file_path)
                logging.info('Файл скачан')
                random_robot = random.choice(ROBOTS)
                try:
                    self._get_robot(random_robot, self.group_id)
                except Exception as error:
                    logging.error('Не удалось отправить стикер: %s', error)
                df = pd.read_csv(file_path, sep=',', encoding='cp1251')
                df.to_csv(
                    file_path,
                    sep=';',
                    index=False,
                    encoding='utf-8'
                )
                await self.client.disconnect()

    def _get_robot(self, robot, chat_id, robot_folder='robot'):
        retries = SEND_MESSAGE_RETRIES

        for attempt in range(1, retries + 1):
            try:
                with open(f'{robot_folder}/{robot}', 'rb') as photo:
                    self.bot.send_sticker(chat_id, photo, timeout=60)
                return
            except FileNotFoundError:
                logging.warning('Робот %s не найден', robot)
                return
            except Exception as error:
                logging.error('Неожиданная ошибка: %s', error)
                if attempt == retries:
                    raise
                time.sleep(2)

    def _make_dir(self, folder_name: str) -> Path:
        path = Path(folder_name)
        path.mkdir(parents=True, exist_ok=True)
        return path

    async def run(self, lifetime_seconds: int):
        await self.client.start()
        logging.info(
            'Telethon клиент запущен. Допустимое время ожидания файла %s сек.',
            lifetime_seconds
        )

        async def timeout():
            await asyncio.sleep(lifetime_seconds)
            if self.client.is_connected():
                logging.info(
                    'Таймаут %s секунд, файл не пришел',
                    lifetime_seconds
                )
                await self.client.disconnect()
        asyncio.create_task(timeout())
        await self.client.run_until_disconnected()
        logging.info('Клиент остановлен')
