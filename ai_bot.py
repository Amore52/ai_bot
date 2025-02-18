from environs import Env
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging
from google.cloud import dialogflow_v2beta1 as dialogflow
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


env = Env()
env.read_env()
bot_token = env.str('TG_BOT_TOKEN')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str('GOOGLE_APPLICATION_CREDENTIALS')


project_id = "amazing-sunset-441112-f0"
session_client = dialogflow.SessionsClient()


async def start(update: Update, context):
    await update.message.reply_text('Здравствуйте!')


async def send_to_dialogflow(update: Update, context):
    user_text = update.message.text
    logger.info(f"Получено сообщение: {user_text}")
    session_id = str(update.message.chat_id)
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=user_text, language_code='ru-RU')
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    dialogflow_response = response.query_result.fulfillment_text
    logger.info(f"Ответ от Dialogflow: {dialogflow_response}")
    await update.message.reply_text(dialogflow_response)

def main():
    application = Application.builder().token(bot_token).build()
    start_handler = CommandHandler('start', start)
    dialogflow_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, send_to_dialogflow)
    application.add_handler(start_handler)
    application.add_handler(dialogflow_handler)
    application.run_polling()

if __name__ == '__main__':
    main()