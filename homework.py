from http import HTTPStatus
from json import JSONDecodeError
import logging
import os
import requests
import telegram
import time
from dotenv import load_dotenv
from requests.exceptions import RequestException
from users_exception import TelegramException


load_dotenv()

name_practicum_token = 'PRACTICUM_TOKEN'
name_telegram_token = 'TELEGRAM_TOKEN'
name_telegram_chat_id = 'CHAT_ID'
PRACTICUM_TOKEN = os.getenv(name_practicum_token)
TELEGRAM_TOKEN = os.getenv(name_telegram_token)
TELEGRAM_CHAT_ID = os.getenv(name_telegram_chat_id)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправить сообщение боту."""
    try:
        obj_msg = bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        raise TelegramException(f'Ошибка при отправке сообщения {error}')
    else:
        logging.info('Отправлено сообщение в чат!')

    if not isinstance(obj_msg, telegram.Message):
        raise TelegramException('Сообщение не отправлено')


def get_api_answer(current_timestamp):
    """Получить ответ API на момент времени."""
    logging.info('Начало получения ответа API')
    request_params = {
        'url': ENDPOINT,
        'params': {
            'from_date': current_timestamp or int(time.time())
        },
        'headers': HEADERS,
    }

    try:
        response = requests.get(**request_params)
    except Exception as error:
        raise RequestException(
            f'Ошибка GET: {request_params}; Текст: {error}'
        )

    if response.status_code != HTTPStatus.OK:
        exception_text = (
            f'Код ответа: {response.status_code}; '
            f'Параметры: {request_params}'
            f'Текст ответа: {response.text}'
        )
        raise RequestException(exception_text)

    try:
        json_answer = response.json()
    except Exception:
        raise JSONDecodeError('Ошибка при разпознавании JSON')
    return json_answer


def check_response(response):
    """Проверить ответ на ожидаемые значения."""
    if not isinstance(response, dict):
        raise TypeError('Ответ response не словарь')

    if 'homeworks' not in response.keys():
        raise KeyError('Ответ response не содержит ключ homeworks')

    if not isinstance(response['homeworks'], list):
        raise TypeError('Ответ response ключ homeworks не список')

    return response['homeworks']


def parse_status(homework):
    """Получить статус задания."""
    if not isinstance(homework, dict):
        raise TypeError('Элемент homework не словарь')

    keys_name = ['homework_name', 'status']
    for key in keys_name:
        if key not in homework.keys():
            raise KeyError(f'homework отсутствует ключ: {key}')

    homework_name = homework[keys_name[0]]
    homework_status = homework[keys_name[1]]
    if homework_status not in HOMEWORK_VERDICTS.keys():
        raise KeyError(f'HOMEWORK_VERDICTS нет ключа: {homework_status}')

    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверить переменные окружения на актуальность."""
    error = any([
        PRACTICUM_TOKEN == '', PRACTICUM_TOKEN is None,
        TELEGRAM_TOKEN == '', TELEGRAM_TOKEN is None,
        TELEGRAM_CHAT_ID == '', TELEGRAM_CHAT_ID is None,
    ])

    if error:
        logging.critical('Не заполнены токены! Работа остановлена')

    return not error


def check_report(report, message, bot=None):
    """Проверка и занесения в report данных по ошибке."""
    logging.error(message)
    if bot is not None and report.current != report.previous:
        send_message(bot, message)
        report.current = report.previous


def main():
    """Основная логика работы бота."""
    logging.basicConfig(
        format=('%(asctime)s - %(levelname)s - %(message)s'
                '- func:%(funcName)s, line:%(lineno)d'),
        level=logging.INFO)
    logging.info('Начата работа бота')
    if not check_tokens():
        exit()

    logging.info('Инициализация бота')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    logging.info('Формирование запроса к API')

    report = {
        'current': 'current',
        'previous': 'previous',
    }

    while True:
        try:
            response = get_api_answer(current_timestamp)
            list_answer = check_response(response)
            for homework in list_answer:
                message_new_status = parse_status(homework)
                send_message(bot, message_new_status)

            if len(list_answer) == 0:
                logging.debug('Нет новых статусов')

            current_timestamp = int(time.time())
        except TelegramException as error:
            check_report(report, f'Ошибка Telegram: {error}')
        except RequestException as error:
            check_report(report, f'HTTPЗапрос вернул код: {error}', bot)
        except KeyError as error:
            check_report(report, f'В словаре {error}', bot)
        except JSONDecodeError as error:
            check_report(
                report,
                f'При получении словаря из response: {error}',
                bot
            )
        else:
            logging.info('Новый запрос к API')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
