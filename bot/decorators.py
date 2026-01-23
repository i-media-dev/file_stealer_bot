import functools
import json
import logging
import time
from datetime import datetime as dt

import psycopg2
from psycopg2 import InterfaceError, OperationalError

from bot.constants import DATE_FORMAT, MAX_RETRIES, TIME_DELAY, TIME_FORMAT
from bot.db_config import config
from bot.logging_config import setup_logging

setup_logging()


def time_of_script(func):
    """Универсальный декоратор для логирования выполнения."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_ts = time.time()
        date_str = dt.now().strftime(DATE_FORMAT)

        print(
            f'Функция {func.__name__} начала работу '
            f'{date_str} в {dt.now().strftime(TIME_FORMAT)}'
        )

        status = 'SUCCESS'
        error_type = error_message = None

        try:
            return await func(*args, **kwargs)

        except Exception as error:
            status = 'ERROR'
            error_type = type(error).__name__
            error_message = str(error)
            raise

        finally:
            exec_time_sec = round(time.time() - start_ts, 3)

            print(
                f'Функция {func.__name__} завершила работу '
                f'в {dt.now().strftime(TIME_FORMAT)}. '
                f'Время выполнения — {round(exec_time_sec / 60, 2)} мин.'
            )

            log_record = {
                "DATE": date_str,
                "STATUS": status,
                "FUNCTION_NAME": func.__name__,
                "EXECUTION_TIME": exec_time_sec,
                "ERROR_TYPE": error_type,
                "ERROR_MESSAGE": error_message,
                "ENDLOGGING": 1
            }

            logging.info(json.dumps(log_record, ensure_ascii=False))

    return wrapper


def time_of_function(func):
    """
    Декоратор для измерения времени выполнения функции.

    Замеряет время выполнения декорируемой функции и логирует результат
    в секундах и минутах. Время округляется до 3 знаков после запятой
    для секунд и до 2 знаков для минут.

    Args:
        func (callable): Декорируемая функция, время выполнения которой
        нужно измерить.

    Returns:
        callable: Обёрнутая функция с добавленной функциональностью
        замера времени.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = round(time.time() - start_time, 3)
        logging.info(
            f'Функция {func.__name__} завершила работу. '
            f'Время выполнения - {execution_time} сек. '
            f'или {round(execution_time / 60, 2)} мин.'
        )
        return result
    return wrapper


def connection_db(func):
    """
    Декоратор для подключения к базе данных.

    Подключается к базе данных, обрабатывает ошибки в процессе подключения,
    логирует все успешные/неуспешные действия, вызывает функцию, выполняющую
    действия в базе данных и закрывает подключение.

    Args:
        func (callable): Декорируемая функция, которая выполняет
        действия с базой данных.

    Returns:
        callable: Обёрнутая функция с добавленной функциональностью
        подключения к базе данных и логирования.
    """
    def wrapper(*args, **kwargs):
        connection = None
        cursor = None
        delay = TIME_DELAY
        max_retries = MAX_RETRIES

        for attempt in range(max_retries):
            try:
                connection = psycopg2.connect(**config)
                cursor = connection.cursor()
                kwargs['cursor'] = cursor
                result = func(*args, **kwargs)
                connection.commit()
                return result
            except (OperationalError, InterfaceError) as error:
                if attempt < max_retries - 1:
                    logging.warning(
                        f'Попытка {attempt + 1} не удалась, '
                        f'повтор через {delay}с: {error}'
                    )
                    time.sleep(delay)
                    continue
                else:
                    logging.error(
                        f'Все {max_retries} попыток подключения не удались'
                    )
                    raise
            except Exception as error:
                if connection:
                    connection.rollback()
                logging.error(
                    'Ошибка в %s: %s',
                    func.__name__,
                    str(error),
                    exc_info=True
                )
                raise
            finally:
                if cursor:
                    cursor.close()
                if connection and not connection.closed:
                    connection.close()
    return wrapper
