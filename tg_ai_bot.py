import logging
import argparse

from environs import Env
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.api_core.exceptions import GoogleAPICallError
from functools import partial

logger = logging.getLogger(__file__)


def setup_bot(project_id):
    env = Env()
    env.read_env()
    bot_token = env.str('TG_BOT_TOKEN')
    session_client = dialogflow.SessionsClient()

    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            partial(handle_text_message, session_client=session_client, project_id=project_id)
        )
    )
    return application


def detect_intent(session_client, project_id, session_id, text, language_code='ru-RU'):
    try:
        session = session_client.session_path(project_id, session_id)
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(session=session, query_input=query_input)
        if response.query_result and response.query_result.fulfillment_text:
            return response.query_result.fulfillment_text
        return None
    except GoogleAPICallError as e:
        logger.error(f'Ошибка при обращении к Dialogflow: {e}')
        return None
    except Exception as e:
        logger.error(f'Произошла ошибка: {e}')
        return None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Здравствуйте!')


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE, session_client, project_id):
    user_text = update.message.text
    logger.info(f'Получено сообщение от пользователя {update.message.chat_id} (проект {project_id}): {user_text}')
    try:
        session_id = f"tgid-{update.message.chat_id}"
        dialogflow_response = detect_intent(session_client, project_id, session_id, user_text)
        if dialogflow_response:
            await update.message.reply_text(dialogflow_response)
        else:
            await update.message.reply_text('Произошла ошибка.')
    except Exception as e:
        logger.error(f'Ошибка при обработке сообщения: {e}')
        await update.message.reply_text('Произошла ошибка.')


def main():
    parser = argparse.ArgumentParser(description='Запуск Telegram бота с Dialogflow.')
    parser.add_argument('--project_id', type=str, required=True, help='ID проекта Dialogflow')
    args = parser.parse_args()
    application = setup_bot(args.project_id)
    application.run_polling()
    logger.info('Бот запущен...')

if __name__ == '__main__':
    main()