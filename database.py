import sqlite3
import logging  
from config import LOGS, DB_FILE, COUNT_LAST_MSG

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")
path_to_db = DB_FILE  # файл базы данных


def create_db(database_name=path_to_db):
    db_path = f'{database_name}'
    connection = sqlite3.connect(db_path)
    connection.close()


def execute_query(sql_query, data=None, db_path=f'{path_to_db}'):
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        if data:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)

        connection.commit()
        connection.close()
    except Exception as e:
        logging.error(e)


def execute_selection_query(sql_query, data=None, db_path=f'{path_to_db}'):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    if data:
        cursor.execute(sql_query, data)
    else:
        cursor.execute(sql_query)
    rows = cursor.fetchall()
    connection.close()
    return rows


# создаём базу данных и таблицу messages
def create_database():
    # подключаемся к базе данных
    query1 = f'''
        CREATE TABLE IF NOT EXISTS limits (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        total_gpt_tokens INTEGER,
        tts_symbols INTEGER,
        stt_blocks INTEGER, 
        time_zone INTEGER DEFAULT 0, 
        debug INTEGER DEFAULT 0);
    '''
    execute_query(query1)
    logging.info("DATABASE: База limits данных создана")

    query2 = '''
        CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        role TEXT,
        messages TEXT, 
        time INTEGER,
        FOREIGN KEY (user_id) REFERENCES limits (user_id));
    '''
    execute_query(query2)
    logging.info("DATABASE: База messages данных создана")


def insert_row(table_name, data: tuple):
    if table_name == "limits":
        sql_query = f"SELECT EXISTS(SELECT 1 FROM limits WHERE user_id = {data[0]})"
        res = execute_selection_query(sql_query)
        if res and res[0] and not res[0][0]:
            sql_query = "INSERT INTO limits (user_id, total_gpt_tokens, tts_symbols, stt_blocks) VALUES (?, ?, ?, ?);"
            execute_query(sql_query, data=data)
    else:
        sql_query = "INSERT INTO messages (user_id, role, messages, time)VALUES (?, ?, ?, ?)"
        execute_query(sql_query, data=data)



def increase_value(table_name, user_id, column, value):
    sql_query = f"UPDATE {table_name} SET {column} = {column} + {value} WHERE user_id = {user_id}"
    execute_query(sql_query)


def update_value(table_name, user_id, column, value):
    sql_query = f"UPDATE {table_name} SET {column} = {value} WHERE user_id = {user_id}"
    execute_query(sql_query)


def get_value(table_name, user_id, column):
    sql_query = f'''SELECT {column} FROM {table_name} WHERE user_id={user_id} ORDER BY id DESC LIMIT 1'''
    res = execute_selection_query(sql_query)
    if res and res[0]:
        return execute_selection_query(sql_query)[0][0]
    return 0


def count_users(user_id):
    sql_query = f'''SELECT COUNT(DISTINCT user_id) FROM limits WHERE user_id <> {user_id}'''
    res = execute_selection_query(sql_query)
    if res and res[0]:
        return execute_selection_query(sql_query)[0][0]
    return 0


def select_n_last_messages(user_id, n_last_messages=COUNT_LAST_MSG):
    sql_query = '''SELECT messages, role FROM messages WHERE user_id=? and (role = 'assistant' OR role = 'user') ORDER BY id DESC LIMIT ?'''
    data = execute_selection_query(sql_query, data=(user_id, n_last_messages))

    messages = []
    if data and data[0]:
            for message in reversed(data):
                messages.append({'text': message[0], 'role': message[1]})
            return messages


def get_all_users():
    sql_query = '''SELECT DISTINCT user_id FROM limits;'''
    return execute_selection_query(sql_query)