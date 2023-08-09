# homework_bot
python telegram bot
## Описание
Телеграмм-бот, помогающий студентам Яндекс.Практикума 
получать информацию о статусе проверки их
домашнего задания

## Установка и запуск


Клонировать репозиторий:
```sh
git clone <https or SSH URL>
```

Перейти в папку проекта:
```sh
cd homework_bot
```

### Запуск проекта


Создать и активировать виртуальное окружение:
```sh
python -m venv venv
source venv/Scripts/activate
```

Обновить pip:
```sh
python3 -m pip install --upgrade pip
```

Установить библиотеки:
```sh
pip install -r requirements.txt
```

Создать файл .env с переменными окружения:
BOT_TOKEN=<Токен бота>
ACCOUNT_ID=<ID чата>
PRACTICUM_TOKEN=<Токен доступа к API>

