import sqlite3

users_table_name = "users"
users_table_setting = f""" CREATE TABLE IF NOT EXISTS {users_table_name} (
                id INTEGER PRIMARY KEY,
                ask_count int NOT NULL CHECK (ask_count >= 0) DEFAULT 1,
                name TEXT NOT NULL,
                phone TEXT
            ); """

questions_table_name = "questions"
questions_table_setting = f"""CREATE TABLE IF NOT EXISTS {questions_table_name} (
                        id INTEGER PRIMARY KEY,
                        ask_count INT NOT NULL CHECK(ask_count >= 0) DEFAULT 0,
                        prompt TEXT NOT NULL,
                        parent_prompt text NOT NULL
                     ); """

table_names = [users_table_name, questions_table_name]
table_statements = [users_table_setting, questions_table_setting]


def main():
    connection = sqlite3.connect('zhurik.db')
    cursor = connection.cursor()

    for table_statement in table_statements:
        cursor.execute(table_statement)

    print("База данных успешно создана. Благодарение Богу!")
    connection.close()


if __name__ == "__main__":
    main()
