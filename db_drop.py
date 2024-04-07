from db_init import table_names, db_connect


def main():
    connection = db_connect()
    cursor = connection.cursor()

    for table_name in table_names:
        drop_statement = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(drop_statement)

    print("База данных успешно сброшена. Господи, помилуй!")
    connection.close()


if __name__ == "__main__":
    main()
