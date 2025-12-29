import logging
from pathlib import Path

import pandas as pd

from bot.constants import FOLDER_NAME
from bot.exceptions import DirectoryCreationError, EmptyFeedsListError
from bot.logging_config import setup_logging

setup_logging()


class FileParser:

    def __init__(self, folder_name: str = FOLDER_NAME):
        self.folder_name = folder_name

    def _get_files_list(self, folder_name: str) -> list:
        """
        Защищенный метод, возвращает список
        названий файлов в переданной директории.
        """
        folder_path = Path(__file__).parent.parent / folder_name
        if not folder_path.exists():
            logging.error('Папка %s не существует', folder_name)
            raise DirectoryCreationError(f'Папка {folder_name} не найдена')
        file_list = [
            folder_path / file.name for file
            in folder_path.iterdir() if file.is_file()
        ]
        if not file_list:
            logging.error('В папке нет файлов')
            raise EmptyFeedsListError('Нет скачанных файлов')
        return file_list

    def parse_file(self):
        result = []
        try:
            files = self._get_files_list(self.folder_name)
            for file in files:
                df = pd.read_csv(file, delimiter=';', encoding='utf-8')
                for _, row in df.iterrows():
                    data = {
                        'number': row.get('number'),
                        'заем_выдан_дата': row.get('Заем_выдан_дата'),
                        'выданная_сумма': row.get('Выданная_сумма'),
                        'продукт': row.get('Продукт'),
                        'регион_проживания': row.get('Регион_проживания'),
                        'stat_campaign': row.get('STAT_CAMPAIGN'),
                        'appmetrica': row.get('APPMETRICA'),
                        'stat_source': row.get('STAT_SOURCE'),
                        'stat_ad_type': row.get('STAT_AD_TYPE'),
                        'stat_system': row.get('STAT_SYSTEM'),
                        'stat_term': row.get('STAT_TERM'),
                        'uf_clb_char': row.get('UF_CLB_CHANNEL'),
                        'stat_info': row.get('STAT_INFO'),
                        'стоимость_тс': row.get('Стоимость_ТС'),
                        'марка_тс': row.get('Марка_тс'),
                        'модель_тс': row.get('Модель_тс'),
                        'год_тс': row.get('Год_тс'),
                        'call1': row.get('call1'),
                        'call1_одобр': row.get('call1_одобрено'),
                        'контроль_данных': row.get('контроль_данных'),
                        'одобрено': row.get('одобрено'),
                        'отказано': row.get('отказано'),
                        'источник': row.get('источник'),
                        'leadid': row.get('leadId')
                    }

                    for key, value in data.items():
                        if pd.isna(value):
                            data[key] = None

                    result.append(data)

                return result
        except Exception as error:
            logging.error('Неожиданная ошибка парсинга данных: %s', error)
