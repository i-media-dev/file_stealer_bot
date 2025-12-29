import os

from dotenv import load_dotenv

load_dotenv()

ROBOTS = [
    'catcher-robot.png',
    'chang-robot.png',
    'cleaner-robot.png',
    'harry-robot.png'
]

FOLDER_NAME = os.getenv('FOLDER_NAME', 'files')
"""Директория для сохранения скачанных файлов."""

TOKEN_TELEGRAM = os.getenv('TOKEN_TELEGRAM')

API_ID = int(os.getenv('TG_API_ID'))

API_HASH = os.getenv('TG_API_HASH')

GROUP_ID = int(os.getenv('TG_GROUP_ID'))

LIFETIME = int(os.getenv('LIFETIME_SECONDS', 300))

DATE_FORMAT = '%Y-%m-%d'
"""Формат даты по умолчанию."""

TIME_FORMAT = '%H:%M:%S'
"""Формат времени по умолчанию."""

TIME_DELAY = 5
"""Время повторного реконнекта к дб в секундах."""

MAX_RETRIES = 5
"""Максимальное количество переподключений к бд."""

TABLE_NAME = 'carmoney_bot_crm'
"""Название модели бд по умолчанию."""

CREATE_REPORTS_TABLE = '''
CREATE TABLE IF NOT EXISTS {table_name} (
    id SERIAL PRIMARY KEY,
    number VARCHAR(50),
    заем_выдан_дата DATE,
    выданная_сумма DECIMAL(20,2) CHECK (выданная_сумма >= 0),
    продукт VARCHAR(255),
    регион_проживания VARCHAR(255),
    stat_campaign VARCHAR(255),
    appmetrica VARCHAR(255),
    stat_source VARCHAR(255),
    stat_ad_type VARCHAR(20),
    stat_system VARCHAR(20),
    stat_term VARCHAR(255),
    uf_clb_char VARCHAR(255),
    stat_info TEXT,
    стоимость_тс DECIMAL(20,2) CHECK (стоимость_тс >= 0),
    марка_тс VARCHAR(255),
    модель_тс VARCHAR(255),
    год_тс INTEGER,
    call1 TIMESTAMP,
    call1_одобр TIMESTAMP,
    контроль_данных TIMESTAMP,
    одобрено TIMESTAMP,
    отказано TIMESTAMP,
    источник VARCHAR(255),
    leadid VARCHAR(255)
);

CREATE INDEX IF NOT EXISTS idx_{table_name}_number ON {table_name} (number);
CREATE INDEX IF NOT EXISTS idx_{table_name}_call1 ON {table_name} (call1);
CREATE INDEX IF NOT EXISTS idx_{table_name}_approved
ON {table_name} (одобрено);
CREATE INDEX IF NOT EXISTS idx_{table_name}_denied ON {table_name} (отказано);
CREATE INDEX IF NOT EXISTS idx_{table_name}_leadid ON {table_name} (leadid);
'''
"""SQL запрос на создание модели бд."""

INSERT_REPORT = '''
INSERT INTO {table_name} (
    number,
    заем_выдан_дата,
    выданная_сумма,
    продукт,
    регион_проживания,
    stat_campaign,
    appmetrica,
    stat_source,
    stat_ad_type,
    stat_system,
    stat_term,
    uf_clb_char,
    stat_info,
    стоимость_тс,
    марка_тс,
    модель_тс,
    год_тс,
    call1,
    call1_одобр,
    контроль_данных,
    одобрено,
    отказано,
    источник,
    leadid
) VALUES (
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
)
'''
"""SQL-запрос на вставку данных в модель бд."""
