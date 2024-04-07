from db_init import questions_table_name, db_connect


get_statistics_statement = f"""
    SELECT parent_prompt, prompt, ask_count
    FROM {questions_table_name}
"""


def main():
    connection = db_connect()
    cursor = connection.cursor()

    cursor.execute(get_statistics_statement)

    rows = cursor.fetchall()

    print("=== Выгрузка из базы данных по теме: Статистика заданных вопросов ===")
    for row in rows:
        print(row)
    print("=== Конец выгрузки; Благодарение Богу! ===")


if __name__ == "__main__":
    main()
