from environs import Env
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = Env()
env.read_env()
bot_token = env.str('TG_BOT_TOKEN')


async def start(update: Update, context):
    await update.message.reply_text('Здравствуйте')


async def echo(update: Update, context):
    user_text = update.message.text
    logger.info(f"Получено сообщение: {user_text}")
    await update.message.reply_text(user_text)


def main():
    application = Application.builder().token(bot_token).build()
    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.run_polling()


if __name__ == '__main__':
    main()