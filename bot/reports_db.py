import logging

from bot.constants import CREATE_REPORTS_TABLE, INSERT_REPORT
from bot.decorators import connection_db
from bot.logging_config import setup_logging

setup_logging()


class ReportDataBase():
    """Класс, предоставляющий интерфейс для работы с базой данных"""
    sql_create_request = CREATE_REPORTS_TABLE
    sql_insert_request = INSERT_REPORT

    def __init__(self, table_name: str):
        self.table_name = table_name

    def _create_table(self, cursor=None) -> None:
        """
        Защищенный метод, создает таблицу в базе данных, если ее не существует.
        Если таблица есть в базе данных - возварщает ее имя.
        """
        try:
            create_table_query = self.sql_create_request.format(
                table_name=self.table_name
            )
            cursor.execute(create_table_query)
            indexes = [
                f'CREATE INDEX IF NOT EXISTS idx_{self.table_name}_number '
                f'ON {self.table_name} (number)',
                f'CREATE INDEX IF NOT EXISTS idx_{self.table_name}_call1 '
                f'ON {self.table_name} (call1)',
                f'CREATE INDEX IF NOT EXISTS idx_{self.table_name}_approved '
                f'ON {self.table_name} (одобрено)',
                f'CREATE INDEX IF NOT EXISTS idx_{self.table_name}_denied '
                f'ON {self.table_name} (отказано)',
                f'CREATE INDEX IF NOT EXISTS idx_{self.table_name}_leadid '
                f'ON {self.table_name} (leadid)',
            ]
            for index_query in indexes:
                cursor.execute(index_query)
            logging.info('Таблица %s успешно создана', self.table_name)
        except Exception as error:
            logging.error(
                'Неожиданная ошибка во время создания таблицы: %s',
                error
            )
            raise

    def insert_report(self, data):
        try:
            query = INSERT_REPORT.format(table_name=self.table_name)
            params = [
                (
                    item['number'],
                    item['заем_выдан_дата'],
                    item['выданная_сумма'],
                    item['продукт'],
                    item['регион_проживания'],
                    item['stat_campaign'],
                    item['appmetrica'],
                    item['stat_source'],
                    item['stat_ad_type'],
                    item['stat_system'],
                    item['stat_term'],
                    item['uf_clb_channel'],
                    item['stat_info'],
                    item['стоимость_тс'],
                    item['марка_тс'],
                    item['модель_тс'],
                    item['год_тс'],
                    item['call1'],
                    item['call1_одобр'],
                    item['контроль_данных'],
                    item['одобрено'],
                    item['отказано'],
                    item['источник'],
                    item['leadid']
                ) for item in data
            ]
            return query, params
        except Exception as error:
            logging.error('Неожиданная ошибка добавления данных: %s', error)
            raise

    @connection_db
    def save_to_database(
        self,
        query_data: tuple,
        cursor=None
    ) -> None:
        """Метод сохраняет обработанные данные в базу данных."""
        try:
            self._drop_tables(cursor)
            self._create_table(cursor)
            query, params = query_data

            if isinstance(params, list):
                cursor.executemany(query, params)
            else:
                cursor.execute(query, params)

            logging.info('✅ Данные успешно сохранены!')
        except Exception as error:
            logging.error(
                'Неожиданная ошибка при сохранении данных: %s',
                error
            )
            raise

    def _drop_tables(self, cursor=None) -> None:
        """Удаляет таблицу полностью."""
        try:
            cursor.execute(f'DROP TABLE IF EXISTS "{self.table_name}" CASCADE')
            logging.info('Таблица %s полностью удалена', self.table_name)
        except Exception as error:
            logging.error('Ошибка удаления таблицы: %s', error)
            raise
