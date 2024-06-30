import os
from dotenv import load_dotenv
from telebot import types
import telebot
import json
from db_init import questions_table_name, db_connect
import hashlib

load_dotenv()
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

bot = telebot.TeleBot(TG_BOT_TOKEN, parse_mode="MARKDOWN")


def parse_json_to_dict(filename):
    with open(filename, encoding="utf-8") as file:
        jsonObj = json.load(file)
        return jsonObj


operators_dict = parse_json_to_dict("./operators.json")
ask_dictionary = parse_json_to_dict("./questions_tree.json")


def form_invite_to_operator_button(name, tag):
    keyboard = types.InlineKeyboardMarkup()
    operator_text = f"{name}"
    tag = format_tag(tag)
    operator_url = f"t.me/{tag}"
    invite_button = types.InlineKeyboardButton(operator_text, operator_url)
    keyboard.add(invite_button)
    return keyboard


def format_tag(tag):
    tag = tag.strip()
    if tag[0] != "@":
        tag = "@" + tag
    return tag


def generate_operators_pool(operators_dict):
    operators_pool = []
    for name, tag in operators_dict.items():
        key = form_invite_to_operator_button(name, tag)
        operators_pool.append(key)
    return operators_pool


def bind_invites_to_operators_dict(operators_dict):
    operators_pool = generate_operators_pool(operators_dict)

    def operator_generator():
        while True:
            for operator_invite_key in operators_pool:
                yield operator_invite_key

    generator = operator_generator()

    def get_next_operator():
        return next(generator)

    return get_next_operator


get_next_operator = bind_invites_to_operators_dict(operators_dict)


def generate_questions_tree_keyboard(questions_tree, parent_chain, answers_dict):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for key, value in questions_tree.items():
        pointer_key = make_pointer_key(key, value, parent_chain[-1])
        if isinstance(value, dict):
            node_keyboard = generate_questions_tree_keyboard(
                value,
                parent_chain + [pointer_key],
                answers_dict
            )
            next_node_button = types.InlineKeyboardButton(
                text=key,
                callback_data=pointer_key
            )

            answers_dict[pointer_key] = node_keyboard
            keyboard.add(next_node_button)
        elif isinstance(value, str):
            end_keyboard = types.InlineKeyboardMarkup(row_width=1)
            start_button = types.InlineKeyboardButton(
                text="В начало",
                callback_data="0"
            )
            back_button = types.InlineKeyboardButton(
                text="Назад",
                callback_data=parent_chain[-1]
            )
            end_keyboard.add(back_button, start_button)
            answer_button = types.InlineKeyboardButton(
                text=key,
                callback_data=pointer_key
            )

            answers_dict[pointer_key] = (value, end_keyboard)
            keyboard.add(answer_button)
            save_question_to_db(pointer_key, parent_chain[-1])
        else:
            raise Exception("Ошибка: не удалось прочитать древо вопросов (встречен неправильный тип данных)")

    if len(parent_chain) > 1:
        go_to_previous_node_button = types.InlineKeyboardButton(
            text="Назад",
            callback_data=parent_chain[-2]
        )
        keyboard.add(go_to_previous_node_button)
    return keyboard


def make_pointer_key(key, value, parent_key):
    pointer_key = repr(id(key)) + "-" + repr(id(value))
    ind = 0
    indexed_question = key + "-" + str(ind)
    continue_generate = True
    while continue_generate:
        indexed_question = key + "-" + str(ind)
        ind += 1
        value_already_there = indexed_questions_dict.get(indexed_question, False)
        continue_generate = bool(value_already_there)
    h = hashlib.new('sha256')
    pointer_key = h.update(indexed_question.encode())
    pointer_key = h.hexdigest()

    sql_names_for_pointer_keys[pointer_key] = indexed_question
    if parent_key is not None:
        parents_for_pointer_key[pointer_key] = parent_key
    questions_for_pointer_keys[pointer_key] = key
    indexed_questions_dict[indexed_question] = True
    return pointer_key


def take_question_from_pointer_key(pointer_key):
    if pointer_key == "0":
        return get_chat_bot_start_text()
    if pointer_key in questions_for_pointer_keys:
        prompt = questions_for_pointer_keys[pointer_key]

        return prompt
    else:
        raise Exception("Запрошен несуществующий ключ вопроса")


def take_sql_name_from_pointer_key(pointer_key):
    if pointer_key in sql_names_for_pointer_keys:
        sql_name = sql_names_for_pointer_keys[pointer_key]
        return sql_name
    else:
        raise Exception("Запрошен несуществующий ключ вопроса")


def take_parent_for_pointer_key(pointer_key):
    return parents_for_pointer_key.get(pointer_key, None)


def take_sql_name_from_parent_of_pointer_key(pointer_key):
    parent_key = take_parent_for_pointer_key(pointer_key)
    return take_sql_name_from_pointer_key(parent_key)


def save_question_to_db(question_key, parent_key):
    connection = db_connect()
    curs = connection.cursor()
    search_statement = f"""
        SELECT id FROM {questions_table_name}
        WHERE prompt = ? AND parent_prompt = ?
    """
    question = take_sql_name_from_pointer_key(question_key)
    parent = take_sql_name_from_pointer_key(parent_key)
    curs.execute(search_statement, [question, parent])
    data = curs.fetchall()
    if len(data) != 0:
        return

    insert_statement = f"""
        INSERT INTO {questions_table_name} (prompt, parent_prompt)
        VALUES (?, ?)
    """
    curs.execute(insert_statement, [question, parent])
    d = curs.fetchall()
    connection.commit()
    connection.close()


def update_question_usage(question_key):
    question = take_sql_name_from_pointer_key(question_key)
    parent = take_sql_name_from_parent_of_pointer_key(question_key)
    connection = db_connect()
    curs = connection.cursor()
    search_statement = f"""
        UPDATE {questions_table_name}
        SET ask_count = ask_count + 1
        WHERE prompt = ? AND parent_prompt = ?
    """

    curs.execute(search_statement, [question, parent])
    connection.commit()
    connection.close()


questions_for_pointer_keys = {}
indexed_questions_dict = {}
parents_for_pointer_key = {}
sql_names_for_pointer_keys = {}
answers_dict = {}


chat_bot_start_point = generate_questions_tree_keyboard(
    ask_dictionary,
    ["0"],
    answers_dict
)
answers_dict["0"] = chat_bot_start_point
print(answers_dict)


@bot.message_handler(commands=['start'])
def any_msg(message):
    send_welcome_message(bot, message)


def send_welcome_message(bot, message):
    bot.send_message(
        message.chat.id,
        "Привет!\n\nЯ чат-бот факультета журналистики УрФУ, с радостью помогу вам узнать о поступлении в 2024 году!\n\n_Я ещё нахожусь на этапе разработки, поэтому если я вдруг перестану отвечать, перезапустите меня командой /start.\nЕсли это не поможет, свяжитесь с разработчиками_"
    )
    bot.send_message(
        message.chat.id,
        get_chat_bot_start_text(),
        reply_markup=chat_bot_start_point
    )


def get_chat_bot_start_text():
    return "О чём бы вы хотели спросить?"


@bot.message_handler(commands=['help'])
def help_msg(message):
    send_invite_to_operator_message(bot, message)


def send_invite_to_operator_message(bot, message):
    invite_text = "Если ваши вопросы остались без ответа, то вы можете обратиться за помощью к нашему оператору:"
    invite_key = get_next_operator()
    bot.send_message(message.chat.id, invite_text, reply_markup=invite_key)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    sign_id = call.data
    if sign_id not in answers_dict:
        return

    answer_data = answers_dict[sign_id]

    theme_text = take_question_from_pointer_key(sign_id)

    if isinstance(answer_data, tuple):
        answer_text = answer_data[0]
        answer_message = f"{theme_text}\n{answer_text}"
        keyboard = answer_data[1]
        update_question_usage(sign_id)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            text=answer_message,
            message_id=call.message.message_id,
            reply_markup=None
        )

        bot.send_message(
            chat_id=call.message.chat.id,
            text="Что-нибудь ещё?",
            reply_markup=keyboard
        )
    else:
        if not (theme_text.endswith("?") or theme_text.endswith(".") or theme_text.endswith("!")):
            theme_text += ":"
        keyboard = answer_data
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            text=theme_text,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )


print("Бот запущен! Слава Богу!")
bot.infinity_polling()
