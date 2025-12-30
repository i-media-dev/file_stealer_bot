import asyncio

from bot.constants import (API_HASH, API_ID, GROUP_ID, LIFETIME, TABLE_NAME,
                           TOKEN_TELEGRAM)
from bot.decorators import time_of_script
from bot.file_parser import FileParser
from bot.reports_db import ReportDataBase
from bot.stealer_client import FileStealerClient


@time_of_script
async def main():
    token = TOKEN_TELEGRAM
    stealer = FileStealerClient(
        token,
        api_id=API_ID,
        api_hash=API_HASH,
        group_id=GROUP_ID,
    )
    await stealer.run(LIFETIME)
    parser_client = FileParser()
    data = parser_client.parse_file()

    db_client = ReportDataBase(TABLE_NAME)
    query_data = db_client.insert_report(data)
    db_client.save_to_database(query_data)


if __name__ == '__main__':
    asyncio.run(main())
