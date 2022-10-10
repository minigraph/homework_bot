from http import HTTPStatus
import logging
import os
import requests
import telegram
import time
from dotenv import load_dotenv
from requests.exceptions import RequestException
from users_exception import TelegramException


load_dotenv()

last_msg = ''
name_practicum_token = 'PRACTICUM_TOKEN'
name_telegram_token = 'TELEGRAM_TOKEN'
name_telegram_chat_id = 'CHAT_ID'
PRACTICUM_TOKEN = os.getenv(name_practicum_token)
TELEGRAM_TOKEN = os.getenv(name_telegram_token)
TELEGRAM_CHAT_ID = os.getenv(name_telegram_chat_id)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO)


def send_message(bot, message):
    """Отправить сообщение боту"""
    global last_msg
    if last_msg != message:
        try:
            bot.send_message(TELEGRAM_CHAT_ID, message)
            logging.info('Отправлено сообщение в чат!')
        except:
            raise TelegramException('Сообщение не отправлено')
        else:
            last_msg = message


def get_api_answer(current_timestamp):
    """Получить ответ API на момент времени"""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        raise RequestException(response.status_code)

    return response.json()


def check_response(response):
    """Проверить ответ на ожидаемые значения"""
    if not isinstance(response, dict):
        raise TypeError('Ответ response не словарь')

    if 'homeworks' not in response.keys():
        raise KeyError('Ответ response не содержит ключ homeworks')

    if not isinstance(response['homeworks'], list):
        raise TypeError('Ответ response ключ homeworks не список')

    return response['homeworks']


def parse_status(homework):
    """Получить статус задания"""
    keys_name = ['homework_name', 'status']
    for key in keys_name:
        if key not in homework.keys():
            raise KeyError(f'homework отсутствует ключ: {key}')

    homework_name = homework[keys_name[0]]
    homework_status = homework[keys_name[1]]
    if homework_status not in HOMEWORK_STATUSES.keys():
        raise KeyError(f'HOMEWORK_STATUSES нет ключа: {homework_status}') 
       
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверить переменные окружения на актуальность"""
    error_list = []
    if PRACTICUM_TOKEN == '' or PRACTICUM_TOKEN is None:
        error_list.append(name_practicum_token)

    if TELEGRAM_TOKEN == '' or TELEGRAM_TOKEN is None:
        error_list.append(name_telegram_token)

    if TELEGRAM_CHAT_ID == '' or TELEGRAM_CHAT_ID is None:
        error_list.append(name_telegram_chat_id)

    if len(error_list):
        logging.critical('Не заполнены токены: {}. Работа остановлена'
                        .format(', '.join(error_list)))

    return len(error_list) == 0


def main():
    """Основная логика работы бота."""
    logging.info('Начата работа бота')
    if not check_tokens():
        return False

    logging.info('Инициализация бота')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    logging.info('Формирование запроса к API')

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
            message = f'Ошибка Telegram: {error}'
            logging.error(message)
        except RequestException as error:
            message = f'HTTPЗапрос вернул код: {error}'
            logging.error(message)
            send_message(bot, message)
        except KeyError as error:
            message = f'В словаре {error}'
            logging.error(message)
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(bot, message)
        else:
            logging.info('Новый запрос к API')
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
