import os
import random
import logging
import vk_api

from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.api_core.exceptions import GoogleAPICallError


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

env = Env()
env.read_env()
VK_TOKEN = env.str("VK_TOKEN")
vk_session = vk_api.VkApi(token=VK_TOKEN)
vk_api = vk_session.get_api()
GOOGLE_APPLICATION_CREDENTIALS = env.str("GOOGLE_APPLICATION_CREDENTIALS")
DIALOGFLOW_PROJECT_ID = env.str("DIALOGFLOW_PROJECT_ID")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
session_client = dialogflow.SessionsClient()


def send_message(user_id: int, message: str) -> None:
    try:
        vk_api.messages.send(
            user_id=user_id,
            message=message,
            random_id=random.randint(1, 1000),
        )
        logger.info(f"Сообщение отправлено пользователю {user_id}: {message}")
    except vk_api.exceptions.VkApiError as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")


def detect_intent_text(session_id: str, text: str, language_code: str = "ru-RU") -> str:
    try:
        session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(session=session, query_input=query_input)
        return response.query_result.fulfillment_text
    except GoogleAPICallError as e:
        logger.error(f"Ошибка при обращении к Dialogflow: {e}")
        return "Произошла ошибка при обработке запроса. Попробуйте позже."


def handle_message(event) -> None:
    user_id = event.user_id
    user_text = event.text
    logger.info(f"Получено сообщение от {user_id}: {user_text}")
    dialogflow_response = detect_intent_text(str(user_id), user_text)
    send_message(user_id, dialogflow_response)


def main() -> None:
    longpoll = VkLongPoll(vk_session)
    logger.info("Бот запущен...")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event)


if __name__ == "__main__":
    main()