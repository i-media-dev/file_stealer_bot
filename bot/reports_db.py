import logging

from bot.constants import CREATE_REPORTS_TABLE, INSERT_REPORT, TABLE_NAME
from bot.decorators import connection_db
from bot.exceptions import TableNameError
from bot.logging_config import setup_logging

setup_logging()


class ReportDataBase():
    """Класс, предоставляющий интерфейс для работы с базой данных"""
    sql_create_request = CREATE_REPORTS_TABLE
    sql_insert_request = INSERT_REPORT

    def __init__(self, table_name: str = TABLE_NAME):
        self.table_name = table_name

    def _allowed_tables(self, cursor) -> list:
        """
        Защищенный метод, возвращает список существующих
        таблиц в базе данных PostgreSQL.
        """
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        return [table[0] for table in cursor.fetchall()]

    @connection_db
    def _create_table_if_not_exists(self, cursor=None) -> str:
        """
        Защищенный метод, создает таблицу в базе данных, если ее не существует.
        Если таблица есть в базе данных - возварщает ее имя.
        """
        try:
            if self.table_name in self._allowed_tables(cursor):
                logging.info('Таблица %s найдена в базе', self.table_name)
                return self.table_name
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
            return self.table_name
        except Exception as error:
            logging.error(
                'Неожиданная ошибка во время создания таблицы: %s',
                error
            )
            raise

    def insert_report(self, data):
        try:
            table_name = self._create_table_if_not_exists()
            query = INSERT_REPORT.format(table_name=table_name)
            params = [
                (
                    item['number'],
                    item['заем выдан дата'],
                    item['выданная сумма'],
                    item['продукт'],
                    item['регион проживания'],
                    item['stat_campaign'],
                    item['appmetrica'],
                    item['stat_source'],
                    item['stat_ad_type'],
                    item['stat_system'],
                    item['stat_term'],
                    item['uf_clb_char'],
                    item['stat_info'],
                    item['стоимость тс'],
                    item['марка тс'],
                    item['модель тс'],
                    item['год тс'],
                    item['call1'],
                    item['call1 одобр'],
                    item['контроль данных'],
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
        """Метод сохраняется обработанные данные в базу данных."""
        try:
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

    @connection_db
    def clean_database(self, cursor=None, **tables: bool) -> None:
        """
        Метод очищает базу данных,
        не удаляя сами таблицы
        """
        try:
            existing_tables = self._allowed_tables()
            for table_name, should_clean in tables.items():
                if should_clean and table_name in existing_tables:
                    cursor.execute(f'DELETE FROM {table_name}')
                    logging.info(f'Таблица {table_name} очищена')
                else:
                    raise TableNameError(
                        'В базе данных отсутствует таблица %s.',
                        table_name
                    )
        except Exception as error:
            logging.error('Ошибка очистки: %s', error)
            raise
