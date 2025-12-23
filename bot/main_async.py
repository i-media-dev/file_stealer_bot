import asyncio

from bot.constants import API_HASH, API_ID, GROUP_ID, LIFETIME, TOKEN_TELEGRAM
from bot.file_parser import FileParser
from bot.reports_db import ReportDataBase
from bot.stealer_client import FileStealerClient


async def main():
    token = TOKEN_TELEGRAM
    stealer = FileStealerClient(
        api_id=API_ID,
        api_hash=API_HASH,
        group_id=GROUP_ID,
        folder_name='downloads',
    )
    await stealer.run(30)
    parser_client = FileParser()
    data = parser_client.parse_file()

    db_client = ReportDataBase()
    query_data = db_client.insert_report(data)
    db_client.save_to_database(query_data)


if __name__ == '__main__':
    asyncio.run(main())
