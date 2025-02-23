import json
import argparse

from google.cloud import dialogflow_v2beta1 as dialogflow


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []
    for part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)
    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message]
    )
    intents_client.create_intent(parent=parent, intent=intent)


def load_phrases(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def main(project_id):
    phrases = load_phrases('questions.json')
    for intent_name, data in phrases.items():
        questions = data['questions']
        answer = data['answer']
        create_intent(project_id, intent_name, questions, [answer])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create Dialogflow intents.')
    parser.add_argument('--project_id', type=str, required=True, help='ID проекта Dialogflow')
    args = parser.parse_args()

    main(args.project_id)