import random
import logging
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.api_core.exceptions import GoogleAPICallError
from vk_api.exceptions import VkApiError
from environs import Env

logger = logging.getLogger(__file__)


def setup_vk_bot(vk_token, project_id):
    vk_session = vk_api.VkApi(token=vk_token)
    vk_api_session = vk_session.get_api()
    session_client = dialogflow.SessionsClient()
    return vk_session, session_client, project_id, vk_api_session


def send_message(vk_api_session, user_id: int, message: str):
    try:
        vk_api_session.messages.send(
            user_id=user_id,
            message=message,
            random_id=random.randint(1, 1000),
        )
        logger.info(f'Сообщение отправлено пользователю {user_id}: {message}')
    except VkApiError as e:
        logger.error(f'Ошибка при отправке сообщения: {e}')


def detect_intent(session_client, project_id: str, session_id: str, text: str, language_code: str = 'ru-RU') -> str:
    try:
        session = session_client.session_path(project_id, f"vkid-{session_id}")
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = session_client.detect_intent(session=session, query_input=query_input)
        return response.query_result.fulfillment_text if not response.query_result.intent.is_fallback else None
    except GoogleAPICallError as e:
        logger.error(f'Ошибка при обращении к Dialogflow: {e}')
        return None


def handle_message(event, session_client, project_id, vk_api_session):
    user_id = event.user_id
    user_text = event.text
    logger.info(f'Получено сообщение от {user_id}: {user_text}')
    dialogflow_response = detect_intent(session_client, project_id, str(user_id), user_text)
    send_message(vk_api_session, user_id, dialogflow_response)


def main():
    env = Env()
    env.read_env()
    vk_token = env.str('VK_TOKEN')
    project_id = env.str('DIALOGFLOW_PROJECT_ID')

    vk_session, session_client, project_id, vk_api_session = setup_vk_bot(vk_token, project_id)
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            handle_message(event, session_client, project_id, vk_api_session)
    logger.info('Бот запущен...')


if __name__ == '__main__':
    main()