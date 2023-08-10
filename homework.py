import http
import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from endpoints import ENDPOINT
from exceptions import (
    InvalidHttpStatus,
    InvalidRequest,
    MessageNotSend,
    UnknownStatus,
    TelegramBotError
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('ACCOUNT_ID')

RETRY_PERIOD = 600
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверка доступности переменных окружения."""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logger.critical('Отсутствует одна/несколько переменных окружения.')
        sys.exit()


def send_message(bot, message):
    """Отправка сообщения в чат."""
    try:
        logger.debug('Отправка сообщения...')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug('Сообщение отправлено')
    except TelegramBotError:
        logger.error('Сообщение не было доставлено')
        raise MessageNotSend('Сообщение не было доставлено')


def get_api_answer(timestamp):
    """Запрос к единственному эндпоинту API-сервиса."""
    try:
        PAYLOAD = {'from_date': timestamp}
        logger.debug(
            'Отправка запроса к эндпоинту, параметры: '
            f'headers =  {HEADERS} и params = {PAYLOAD}'
        )
        response = requests.get(ENDPOINT, headers=HEADERS, params=PAYLOAD)
        if response.status_code != http.HTTPStatus.OK:
            logger.error('Ошибка запроса')
            raise InvalidHttpStatus('Статус HTTP-кода не равен 200')
        return response.json()
    except Exception as error:
        logger.error(f'Ошибка получения request - {error}')
        raise InvalidRequest('Ошибка получения request')


def check_response(response):
    """Проверка ответа API."""
    try:
        if not isinstance(response, dict):
            logger.error('Запрос к API вернул не словарь')
            raise TypeError('Запрос к API вернул не словарь')
        if 'homeworks' not in response:
            logger.error('Нет ключа homeworks')
            raise KeyError('Нет ключа homeworks')
        if not isinstance(response['homeworks'], list):
            logger.error('Значение ключа homeworks не list')
            raise TypeError('Значение ключа homeworks не list')
        if not response['homeworks']:
            logger.error('Список пуст')
            raise TypeError('Список пуст')
        return response['homeworks']
    except Exception as error:
        logger.error(error)
        raise TypeError(error)


def parse_status(homework):
    """Получаем статус последней домашней работы (если она есть)."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')

    if homework_name is None or status is None:
        raise KeyError('Нет ключей')

    if status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS[status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'

    logger.error(
        f'Неожиданный статус домашней работы: {status},'
        'обнаруженный в ответе API'
    )
    raise UnknownStatus('Hеизвестный статус')


def main():
    """Основная логика работы бота."""
    check_tokens()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            bot.send_message(TELEGRAM_CHAT_ID, message)

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='logging_for_homework.log',
        format='%(asctime)s -%(levelname)s - %(name)s - %(message)s'
    )
    main()
