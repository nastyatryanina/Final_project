import requests, logging
from creds import get_creds
from config import LOGS

logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

URL = f"https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
IAM_TOKEN, FOLDER_ID = get_creds()

def text_to_speech(text):
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}'
    }
    data = {'text': text,
            'lang': "ru-RU",
            'voice': "jane",
            'emotion': "neutral",
            'folderId': FOLDER_ID
    }

    response = requests.post(URL, headers=headers, data=data)
    
    if response.status_code == 200:
        return True, response.content, response.status_code
    else:
        logging.error(response.content)
        return False, "При запросе в SpeechKit возникла ошибка", response.status_code
    

def speech_to_text(data):
    params = "&".join([
        "topic=general",
        f"folderId={FOLDER_ID}",
        "lang=ru-RU"
    ])

    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }

    response = requests.post(
        f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
        headers=headers,
        data=data
    )

    decoded_data = response.json()

    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result"), response.status_code
    else:
        logging.error(response.content)
        return False, "При запросе в SpeechKit возникла ошибка", response.status_code
