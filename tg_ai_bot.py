import os
import logging

from environs import Env
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google.cloud import dialogflow_v2beta1 as dialogflow


logger = logging.getLogger(__file__)


def setup_bot():
    env = Env()
    env.read_env()
    BOT_TOKEN = env.str('TG_BOT_TOKEN')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = env.str('GOOGLE_APPLICATION_CREDENTIALS')
    DIALOGFLOW_PROJECT_ID = 'amazing-sunset-441112-f0'
    session_client = dialogflow.SessionsClient()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text('Здравствуйте!')

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_text = update.message.text
        logger.info(f'Получено сообщение: {user_text}')
        try:
            session_id = f"tgid-{update.message.chat_id}"
            session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)
            text_input = dialogflow.TextInput(text=user_text, language_code='ru-RU')
            query_input = dialogflow.QueryInput(text=text_input)
            response = session_client.detect_intent(session=session, query_input=query_input)
            dialogflow_response = response.query_result.fulfillment_text
            logger.info(f'Ответ от Dialogflow: {dialogflow_response}')
            await update.message.reply_text(dialogflow_response)
        except Exception as e:
            logger.error(f'Ошибка при обработке сообщения: {e}')
            await update.message.reply_text('Произошла ошибка. Попробуйте позже.')

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info('Бот запущен...')
    return application

def main():
    application = setup_bot()
    application.run_polling()

if __name__ == '__main__':
    main()