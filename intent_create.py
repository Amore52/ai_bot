import json
from google.cloud import dialogflow_v2beta1 as dialogflow
from environs import Env


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = [
        dialogflow.Intent.TrainingPhrase(parts=[dialogflow.Intent.TrainingPhrase.Part(text=part)])
        for part in training_phrases_parts
    ]
    message = dialogflow.Intent.Message(text=dialogflow.Intent.Message.Text(text=message_texts))
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )
    intents_client.create_intent(parent=parent, intent=intent)


def load_phrases(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def main():
    env = Env()
    env.read_env()
    project_id = env.str('DIALOGFLOW_PROJECT_ID')

    phrases = load_phrases('questions.json')
    for intent_name, data in phrases.items():
        create_intent(project_id, intent_name, data['questions'], [data['answer']])


if __name__ == '__main__':
    main()