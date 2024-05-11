import csv
import datetime
from openpyxl import Workbook
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

    filepath_without_ext = f"./stats/{generate_statfile_name()}"
    filepath = f"{filepath_without_ext}.csv"

    wb = Workbook()
    excel_writer = wb.active
    with open(filepath, 'w', newline='') as csvfile:
        print("=== Выгрузка из базы данных по теме: Статистика заданных вопросов ===")

        csv_writer = csv.writer(
            csvfile,
            delimiter='|',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL
        )
        headers = ['Вопрос-ID', 'Тема-ID', 'Запросы']
        # печатаем колонки в консоли в обратном порядке
        # для простоты отображения

        print(",\t".join(reversed(headers)))
        csv_writer.writerow(headers)
        excel_writer.append(headers)
        for row in rows:
            print(",\t".join(str(item) for item in reversed(row)))
            csv_writer.writerow(row)
            excel_writer.append(row)

        print("=== Конец выгрузки; Благодарение Богу! ===")

    wb.save(f'{filepath_without_ext}.xlsx')

    connection.close()


if __name__ == "__main__":
    main()
