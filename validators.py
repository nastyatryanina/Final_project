from config import LOGS, MAX_USERS, MAX_USER_STT_BLOCKS, MAX_USER_TTS_SYMBOLS, MAX_USER_GPT_TOKENS, MAX_TTS_SYMBOLS_IN_MESSAGE, MAX_GPT_TOKENS_IN_MESSAGE
from database import get_value, count_users
from gpt import count_gpt_tokens
import math, logging

logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

def is_users_limit(user_id):
    users = count_users(user_id)
    if users >= MAX_USERS:
        logging.info(f"Пользователя с id {user_id} не получилось добавить")
        return False, "К сожалению, лимит пользователей исчерпан."
    logging.info(f"Новый пользователь с id {user_id}")
    return True, ""


def is_tts_symbol_limit(user_id, text):
    text_symbols = len(text)
    all_symbols = get_value("limits", user_id, "tts_symbols") + text_symbols

    if all_symbols >= MAX_USER_TTS_SYMBOLS:
        msg = f"Превышен общий лимит SpeechKit TTS {MAX_USER_TTS_SYMBOLS}. Использовано: {all_symbols} символов. Доступно: {MAX_USER_TTS_SYMBOLS - all_symbols}"
        return False, msg

    if text_symbols >= MAX_TTS_SYMBOLS_IN_MESSAGE:
        msg = f"Превышен лимит SpeechKit TTS на запрос {MAX_TTS_SYMBOLS_IN_MESSAGE}, в сообщении {text_symbols} символов"
        return False, msg

    return True, ""


def is_stt_block_limit(message, duration):
    user_id = message.from_user.id

    audio_blocks = math.ceil(duration / 15)

    all_blocks = get_value("limits", user_id, "stt_blocks") + audio_blocks

    if duration >= 30:
        msg = "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        return False, msg

    if all_blocks >= MAX_USER_STT_BLOCKS:
        msg = f"Превышен общий лимит SpeechKit STT {MAX_USER_STT_BLOCKS}. Использовано {all_blocks} блоков. Доступно: {MAX_USER_STT_BLOCKS - all_blocks}"
        return False, msg

    return True, audio_blocks


def is_gpt_token_limit(user_id, text):
    tokens_in_text, error_code = count_gpt_tokens([{'role': 'user', 'text': text}])
    if tokens_in_text == 0 or error_code != 200:
        msg = f"Не получилось посчитать токены в сообщении"
        return False, msg, error_code
    all_tokens = get_value("limits", user_id, "total_gpt_tokens") + tokens_in_text

    if tokens_in_text >= MAX_GPT_TOKENS_IN_MESSAGE:
        msg = f"Превышен лимит Yandex GPT на запрос {MAX_GPT_TOKENS_IN_MESSAGE}, в сообщении {tokens_in_text} символов"
        return False, msg, error_code

    if all_tokens >= MAX_USER_GPT_TOKENS:
        msg = f"Превышен общий лимит Yandex GPT {MAX_USER_GPT_TOKENS}. Использовано {all_tokens} блоков. Доступно: {MAX_USER_GPT_TOKENS- all_tokens}"
        return False, msg, error_code
    
    return True, all_tokens, error_code

