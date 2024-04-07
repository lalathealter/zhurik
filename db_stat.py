import csv, datetime
from db_init import questions_table_name, db_connect


get_statistics_statement = f"""
    SELECT prompt, parent_prompt, ask_count
    FROM {questions_table_name}
"""


def generate_statfile_name():
    time_format = "%d %b %Y %H-%M-%S"
    now_time = datetime.datetime.now()
    time_string = now_time.strftime(time_format)
    return f"questions_table_statistics - {time_string}"


def main():
    connection = db_connect()
    cursor = connection.cursor()

    cursor.execute(get_statistics_statement)
    rows = cursor.fetchall()

    filepath = f"./stats/{generate_statfile_name()}.csv"
    with open(filepath, 'w', newline='') as csvfile:
        print("=== Выгрузка из базы данных по теме: Статистика заданных вопросов ===")

        spamwriter = csv.writer(
            csvfile,
            delimiter='|',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL
        )
        spamwriter.writerow(['Вопрос', 'Тема', 'Запросы'])
        for row in rows:
            print(row)
            spamwriter.writerow(row)

        print("=== Конец выгрузки; Благодарение Богу! ===")

    connection.close()


if __name__ == "__main__":
    main()
