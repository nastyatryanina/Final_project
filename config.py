MAX_USERS = 4  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 30  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 10  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 500  # 5 000 символов
MAX_USER_GPT_TOKENS = 500  # 2 000 токенов
MAX_TTS_SYMBOLS_IN_MESSAGE = 500
MAX_GPT_TOKENS_IN_MESSAGE = 500

SYSTEM_PROMPT = [{'role': 'system', 'text': 'Помоги подобрать город для путешествия, исходя из пожеланий человека.'
                  'В ответе укажи один лучший город для поездки'}]  # список с системным промтом 

REMIND_TIME = 20 #время, в которое нужно делать рассылку сообщений

HOME_DIR = '/home/student/gpt_bot'  # путь к папке с проектом
LOGS = f'{HOME_DIR}/logs.txt'  # файл для логов
DB_FILE = f'{HOME_DIR}/user_info.db'  # файл для базы данных

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'  # файл для хранения bot_token
