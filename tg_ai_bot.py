import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.api_core.exceptions import GoogleAPICallError
from functools import partial
from environs import Env

logger = logging.getLogger(__file__)


def setup_bot(bot_token, project_id):
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
        return response.query_result.fulfillment_text if response.query_result else None
    except GoogleAPICallError as e:
        logger.error(f'Ошибка при обращении к Dialogflow: {e}')
        return None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Здравствуйте!')


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE, session_client, project_id):
    user_text = update.message.text
    logger.info(f'Получено сообщение от пользователя {update.message.chat_id} (проект {project_id}): {user_text}')
    try:
        session_id = f"tgid-{update.message.chat_id}"
        dialogflow_response = detect_intent(session_client, project_id, session_id, user_text)
        await update.message.reply_text(dialogflow_response or 'Произошла ошибка.')
    except Exception as e:
        logger.error(f'Ошибка при обработке сообщения: {e}')
        await update.message.reply_text('Произошла ошибка.')


def main():
    env = Env()
    env.read_env()
    bot_token = env.str('TG_BOT_TOKEN')
    project_id = env.str('DIALOGFLOW_PROJECT_ID')

    application = setup_bot(bot_token, project_id)
    application.run_polling()
    logger.info('Бот запущен...')


if __name__ == '__main__':
    main()