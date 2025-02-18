#  Telegram, Vkontakte - AI Bot

Этот проект представляет собой двух чат-ботов для платформ VK и Telegram, которые используют Google Dialogflow для обработки естественного языка и генерации ответов. Боты могут отвечать на вопросы пользователей, используя предварительно обученные интенты (intents) в Dialogflow.

## 1.Установка и настройка

### Клонируйте репозиторий:

```
git clone https://github.com/ваш-username/devman_ai_bot.git
cd devman_ai_bot
```
### Создайте виртуальное окружение и установите зависимости:
```
python -m venv .venv
source .venv/bin/activate  # Для Linux/MacOS
# .venv\Scripts\activate    # Для Windows
pip install -r requirements.txt
```
### Настройка Dialogflow:
* Создайте агента в Dialogflow.
* Скачайте API данные `credentials.json` и поместите в директорию проекта.

### Настройте переменные окружения:
```
VK_TOKEN=ваш_токен_vk
TG_BOT_TOKEN=ваш_токен_telegram
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
DIALOGFLOW_PROJECT_ID=ваш_project_id
```

* `VK_TOKEN` — токен доступа для VK API.
* `TG_BOT_TOKEN` — токен для Telegram бота.
* `GOOGLE_APPLICATION_CREDENTIALS` — путь к файлу credentials.json.
* `DIALOGFLOW_PROJECT_ID` — ID вашего проекта в Google Cloud.

## 2.Запуск ботов

Для запуска Telegram бота выполните:
```commandline
python tg_ai_bot.py
```
Для запуска VK бота выполните:
```commandline
python vk_ai_bot.py
```
## 3.Функциональность
### Telegram бот:
* Отвечает на команду /start приветственным сообщением.
* Обрабатывает текстовые сообщения пользователей и отправляет ответы, сгенерированные Dialogflow.
### VK бот:
* Обрабатывает текстовые сообщения пользователей и отправляет ответы, сгенерированные Dialogflow.

## 4. Примеры использования
### Telegram
1. Пользователь отправляет сообщение: "Как устроиться к вам на работу?"

2. Бот отвечает: "Если вы хотите устроиться к нам, напишите на почту game-of-verbs@gmail.com мини-эссе о себе и прикрепите ваше портфолио."

### VK
1. Пользователь отправляет сообщение: "Забыл пароль"

2. Бот отвечает: "Если вы не можете войти на сайт, воспользуйтесь кнопкой «Забыли пароль?» под формой входа. Вам на почту прийдёт письмо с дальнейшими инструкциями. Проверьте папку «Спам», иногда письма попадают в неё."

## Обучение бота

Используйте `intent_create.py` для создания интентов на основе данных из `questions.json`.
```
python intent_create.py
```