# Проект telegram_bot
### Описание
Перед Вами проект Telegram Bot. Учебный проект Яндекс.Практикум.
Проект ставит перед собой цели создания бота, реализующего функционал:
* раз в 900 секунд опрашивать API сервиса Яндекс.Практикум, проверять статус отправленной на ревью работы;
* при изменении статуса анализировать ответ API и отправлять соответствующее уведомление в Telegram;
* логировать свою работу и сообщать о важных проблемах сообщением в Telegram

Использовано:
* Python v.3.7.5 (https://docs.python.org/3.7/)
* Python-dotenv v.0.19.0 (https://pypi.org/project/python-dotenv/0.19.0/)
* Python-telegram-bot v.13.7 (https://docs.python-telegram-bot.org/en/v13.7/telegram.bot.html)
* Flake 8 v.3.9.2 (https://buildmedia.readthedocs.org/media/pdf/flake8/stable/flake8.pdf)
* Pytest v.6.2.5 (https://pypi.org/project/pytest/6.2.5/)

### Установка:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/minigraph/homework_bot.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

Обновите PIP, дабы избежать ошибок установки зависимостей:

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Запустить проект:

```
python3 homework.py
```

### Настройка среды
##### Настройка переменных:
Создайте файл ".env" в основной папке, со следующим содержанием(использованы примеры ключей):
```
PRACTICUM_TOKEN=a0_AAAAAAA0AaAAAAAaaAAAAAAAAAAAaAAAAaaAAAA0Aaa0aaAa0aAAaAA
TELEGRAM_TOKEN=1111111111:AAAA0aAa00aaAaAA_AAAAaAaA0A_AAaAaaa
CHAT_ID=111111111
```
PRACTICUM_TOKEN необходимо получить у поддержки Яндекс.Практикум.

##### Настройка бота:
Создание аккаунта бота:
* Найдите бота @BotFather
* Зарегистрируйте бота, получите токен, это TELEGRAM_TOKEN

##### Получение ID получателя сообщений:
* Найдите бота @userinfobot
* Запустите бота, отправьте сообщение получателя, это CHAT_ID

### Автор:
* Михаил Никитин
* * tlg: @minigraf 
* * e-mail: minigraph@yandex.ru;
