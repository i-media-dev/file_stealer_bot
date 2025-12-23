from dotenv import load_dotenv

from bot.constants import GROUP_ID, LIFETIME, TOKEN_TELEGRAM
from bot.file_parser import FileParser
from bot.reports_db import ReportDataBase
from bot.stealer_bot import FileStealer

load_dotenv()


def main():
    token = TOKEN_TELEGRAM

    if not token:
        raise ValueError('Отсутствует токен в переменных окружения')

    chat_id = GROUP_ID

    if not chat_id:
        raise ValueError('Отсутствует ID чата в переменных окружения')

    file_stealer = FileStealer(token, chat_id)
    file_stealer.run(LIFETIME)

    parser_client = FileParser()
    data = parser_client.parse_file()

    db_client = ReportDataBase()
    query_data = db_client.insert_report(data)
    db_client.save_to_database(query_data)


if __name__ == '__main__':
    main()
