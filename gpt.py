import requests
import logging 
from config import LOGS, MAX_GPT_TOKENS, SYSTEM_PROMPT
from creds import get_creds

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

IAM_TOKEN, FOLDER_ID = get_creds()
# подсчитываем количество токенов в сообщениях
def count_gpt_tokens(messages):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{FOLDER_ID}/yandexgpt/latest",
        "messages": messages
    }
    response = requests.post(url=url, json=data, headers=headers)
    if response.json().get("tokens") is not None:
        return len(response.json()["tokens"]), response.status_code
    else:
        logging.error(response.json())  # если ошибка - записываем её в логи
        return 0, response.status_code

# запрос к GPT
def ask_gpt(messages):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": MAX_GPT_TOKENS
        },
        "messages": SYSTEM_PROMPT + messages
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        logging.error(response.content)
        return False, f"Ошибка при обращении к GPT", None, response.status_code
    
    answer = response.json()['result']['alternatives'][0]['message']['text']
    tokens_in_answer, error_code = count_gpt_tokens([{'role': 'assistant', 'text': answer}])
    if tokens_in_answer == 0 or error_code != 200:
        return False, "Ошибка при ображении к tokinize", None, error_code
    
    return True, answer, tokens_in_answer, response.status_code
    
