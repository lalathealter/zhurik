import os
from dotenv import load_dotenv
from telebot import types
import telebot
import json
import sqlite3
from db_init import questions_table_name

load_dotenv()
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

bot = telebot.TeleBot(TG_BOT_TOKEN)


def parse_json_to_dict(filename):
    with open(filename) as file:
        jsonObj = json.load(file)
        return jsonObj


ask_dictionary = parse_json_to_dict("./questions_tree.json")
db_conn = sqlite3.connect('zhurik.db')


def generate_questions_tree_keyboard(questions_tree, parent_chain, answers_dict):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for key, value in questions_tree.items():
        pointer_key = make_pointer_key(key, value)
        if isinstance(value, dict):
            node_keyboard = generate_questions_tree_keyboard(value, parent_chain + [pointer_key], answers_dict)
            next_node_button = types.InlineKeyboardButton(text=key, callback_data=pointer_key)

            answers_dict[pointer_key] = node_keyboard
            keyboard.add(next_node_button)
        elif isinstance(value, str):
            end_keyboard = types.InlineKeyboardMarkup(row_width=1)
            start_button = types.InlineKeyboardButton(text="В начало", callback_data="0")
            back_button = types.InlineKeyboardButton(text="Назад", callback_data=parent_chain[-2])
            end_keyboard.add(start_button, back_button)
            answer_button = types.InlineKeyboardButton(text=key, callback_data=pointer_key)

            answers_dict[pointer_key] = (value, end_keyboard)
            keyboard.add(answer_button)
            save_question_to_db(key, parent_chain[-1])
        else:
            raise Exception("Ошибка: не удалось прочитать древо вопросов (встречен неправильный тип данных)")

    if len(parent_chain) > 1:
        go_to_previous_node_button = types.InlineKeyboardButton(text="Назад", callback_data=parent_chain[-2])
        keyboard.add(go_to_previous_node_button)
    return keyboard

def make_pointer_key(key, value):
    return key + "-" + repr(id(value))

def take_value_from_pointer_key(pointer_key):
    return pointer_key.split("-")[1]


def save_question_to_db(question, parent, db_connection):
    with db_connection.cursor() as curs:
        search_statement = f"""
            SELECT id FROM {questions_table_name}
            WHERE prompt = ? AND parent_prompt = ?
        """
        curs.execute(search_statement, question, parent)
        data = curs.fetchall()
        if len(data) == 0:
            return

        insert_statement = f"""
            INSERT INTO {questions_table_name} (prompt, parent_prompt)
            VALUES (?, ?)
        """
        curs.execute(insert_statement, question, parent)
    db_connection.commit()


answers_dict = {}
chat_bot_start_point = generate_questions_tree_keyboard(ask_dictionary, ["0"], answers_dict)
answers_dict["0"] = chat_bot_start_point
print(answers_dict)


@bot.message_handler(commands=['start'])
def any_msg(message):
    global chat_bot_start_point
    send_welcome_message(bot, message)

def send_welcome_message(bot, message):
    bot.send_message(
        message.chat.id,
        "Привет! Спроси меня о чём угодно", 
        reply_markup=chat_bot_start_point
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    sign_id = call.data
    global answers_dict
    answer = answers_dict[sign_id]
    if isinstance(answer, tuple):
        msg = answer[0]
        keyboard = answer[1]
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            text=msg,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            text=call.message.text,
            message_id=call.message.message_id,
            reply_markup=answer
        )

print("Бот запущен! Слава Богу!")
bot.infinity_polling()
