import telebot, logging, schedule, random, time
from datetime import datetime
from threading import Thread
from speechkit import text_to_speech, speech_to_text
from gpt import ask_gpt
from config import LOGS, REMIND_TIME
from creds import get_bot_token
import database as db
import validators


logging.basicConfig(filename=LOGS,
                    level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s",
                    filemode="w")

TOKEN = get_bot_token()
bot = telebot.TeleBot(TOKEN)

db.create_db()
db.create_database()

start_message = ("Я бот-помощник для путешествий.\n"
                 "Отправь мне голосовое или текстовое сообщение со своими пожеланиями по путешествию просто в чат(никаких комманд перед этим вводить не нужно).\n" 
                 "Можешь посмотреть весь список функций по команде /help (лучше сделай это прежде, чем пользоваться ботом)")

functions = {
    '/set_time_zone': "Указать разницу во времени с Москвой",
    '/tts': "Проверка работы режима TextToSpeech", 
    '/stt': "Проверка работы режима SpeechToText",
}

remind_messages = [
    ("Тебя уже давно не видно 🥺..."
    "Можешь еще поспрашивать нашего бота про разные города, даже если не планируешь туда поехать🌆 "), 
    ("Откройте для себя новые направления с нашим телеграм-ботом! "
     "Путешествуйте с комфортом и находите лучшие места для отдыха."),
    ("Не упустите возможность отправиться в незабываемое путешествие! "
    "Наш телеграм-бот поможет вам найти самые интересные места для посещения."), 
    ("Путешествуйте с умом! Откройте для себя уникальные места вместе с нашим телеграм-ботом."), 
    ("Исследуйте мир с нашим ботом! Он поможет вам найти лучшие места для отдыха и приключений"), 
    ("Откройте для себя новые горизонты с нашим ботом! Путешествуйте с комфортом и находите незабываемые места для отдыха"), 
    ("Наслаждайтесь путешествиями с нашим ботом! "
     "Он поможет вам найти самые интересные места для посещения и сделает ваше путешествие незабываемым."), 
    ("Откройте для себя мир с нашим ботом! Путешествуйте с удовольствием и находите лучшие места для отдыха."), 
    ("Исследуйте новые страны с нашим ботом! "
     "Он поможет вам найти уникальные места и сделать ваше путешествие особенным."),
    ("Откройте для себя новые приключения с нашим ботом! Путешествуйте с комфортом и находите лучшие места для отдыха."), 
    ("Наслаждайтесь путешествиями с нашим ботом! Он поможет вам найти самые интересные места для посещения и сделает ваше путешествие незабываемым.")
]

def create_keyboard(buttons_list):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons_list)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id

    logging.info(f"Новый пользователь с id {user_id}")

    status, error_message = validators.is_users_limit(user_id) #проверка на количество пользователей

    if not status:
        bot.send_message(user_id, error_message)
        return

    bot.send_message(user_id, f"Привет {message.from_user.first_name}!" + start_message,
                         reply_markup=create_keyboard(['/help']))

    db.insert_row("limits", (user_id, 0, 0, 0))


@bot.message_handler(commands=['set_time_zone'])
def set_time_zone(message):
    bot.send_message(message.chat.id, "Введи следующим сообщением целое число в диапозоне от -12 до 12.")
    bot.register_next_step_handler(message, get_time_zone)


def get_time_zone(message):
    hour = message.text
    try:
        hour = int(hour)       
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат. Попробую еще раз ввести целое число в диапозоне от -12 до 12.")
        bot.register_next_step_handler(message, get_time_zone)
        return

    if not -12 <= hour <= 12 :
        bot.send_message(message.chat.id, "Неверный формат. Попробую еще раз ввести целое число в диапозоне от -12 до 12.")
        bot.register_next_step_handler(message, get_time_zone)
        return
    
    db.update_value('limits', message.chat.id, 'time_zone', hour)
    bot.send_message(message.chat.id, "Мы учтем временной пояс, чтобы не беспокоить вас не вовремя.", reply_markup=create_keyboard(['/help']))

@bot.message_handler(commands=['help'])
def help(message):
    user_id = message.chat.id
    help_message = ""
    for func in functions.items():
        help_message += f'{func[0]} - {func[1]}\n'
    bot.send_message(user_id, help_message)


@bot.message_handler(commands=['tts'])
def tts_handler(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Отправь следующим сообщением текст, чтобы я его озвучил!')
    bot.register_next_step_handler(message, tts, None, None)


def tts(message, arg_user_id, arg_text):
    if message != None:
        user_id = message.chat.id
        text = message.text
    else:
        user_id = arg_user_id
        text = arg_text

    try: 
        if message != None and message.content_type != 'text':
            bot.send_message(user_id, 'Отправь текстовое сообщение')
            return

        status, error_message = validators.is_tts_symbol_limit(user_id, text)
        if not status:
            bot.send_message(user_id, error_message)
            return
         
        db.increase_value("limits", user_id, "tts_symbols", len(text))
        logging.info(f"Запрос от {user_id} проверки режима TTS")

        status, content = text_to_speech(text)

        if status:
            bot.send_voice(user_id, content)
        else:
            bot.send_message(user_id, content)
    except Exception as e:
        logging.error(e)  
        bot.send_message(user_id, 
                         "Не получилось перевест текст в аудио. Попробуй еще ввести текст вместо голосового сообщения.")


@bot.message_handler(commands=['stt'])
def stt_handler(message):
    bot.send_message(message.chat.id, "Отправь голосовое сообщение: ")
    
    bot.register_next_step_handler(message, stt)


def stt(message, mode="send"):
    try:
        user_id = message.from_user.id

        if not message.voice:
            bot.send_message(user_id, 'Отправь голосовое сообщение')
            return False, ""

        status, out = validators.is_stt_block_limit(message, message.voice.duration)
        if not status:
            bot.send_message(user_id, out)
            return False, ""

        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)

        status, text = speech_to_text(file)

        if status:
            db.increase_value("limits", user_id, "stt_blocks", out) #увеличить счетчик блоков

        if status and mode == "send":
            bot.send_message(user_id, text, reply_to_message_id=message.id)
        elif not status:
            bot.send_message(user_id, text)
        
        return status, text
    except Exception as e:
        logging.error(e)  
        bot.send_message(message.from_user.id, "Не получилось перевести аудио. Попробуй еще раз.")
        return False, ""
    
    
@bot.message_handler(content_types=['text'])
def get_gpt_answer(message, arg_user_id=None, arg_text=None, mode="send") -> tuple[bool, str]:
    if message != None:
        user_id = message.from_user.id
        text = message.text
    else:
        user_id = arg_user_id
        text = arg_text

    try:
        status, out = validators.is_gpt_token_limit(user_id, text)

        if not status:
            bot.send_message(user_id, out)
            return False, ""
        
        db.insert_row("messages", (user_id, "user", text, int(time.time())))
        messages = db.select_n_last_messages(user_id) 
        print("here")
        status, answer, tokens_in_answer = ask_gpt(messages)
        if not status:
            bot.send_message(user_id, text)
            return False, ""

        db.increase_value("limits", user_id,  "total_gpt_tokens", tokens_in_answer)
        db.insert_row("messages", (user_id, "assistant", answer, int(time.time())))

        if mode == "send":
            bot.send_message(user_id, answer)
        return True, answer
    
    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")
        return False, ""

        

@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    status, text = stt(message, mode="return")
    if not status:
        return
    
    status, answer = get_gpt_answer(None, message.from_user.id, text, mode = "return")

    tts(None, message.from_user.id, answer)


@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.from_user.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")


def remind():
    all_users = db.get_all_users()
    for user in all_users:
        user_zone = db.get_value('limits', user[0], 'time_zone')
        last_msg = db.get_value('messages', user[0], 'time')

        #если сейчас время с учетом разницы пользователя = REMIND_TIME и с момента отправки последнего сообщения прошло больше дня
        if last_msg != None and datetime.fromtimestamp(user_zone*3600 + last_msg).hour ==  REMIND_TIME and time.time() - last_msg >= 86400: 
            bot.send_message(user[0], random.choice(remind_messages))
            db.insert_row('messages', (user[0], 'bot', "", int(time.time())))


def schedule_runner(): 
    while True: 
        schedule.run_pending() 
        time.sleep(1)

schedule.every().hour.do(remind)

Thread(target = schedule_runner).start()

bot.polling()