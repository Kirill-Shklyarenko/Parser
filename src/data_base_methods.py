import psycopg2


def connection() -> any:
    conn = psycopg2.connect(dbname='telemetry', user='postgres',
                            password='123', host='localhost')
    conn.autocommit = True
    cur = conn.cursor()
    return cur, conn


def execute(data_to_insert: list, table_name: str, cur):
    # Преобразование типов (int ---> bool)
    for string in data_to_insert:
        if 'isFake' in string[0]:
            string[1] = bool(string[1])
        if 'hasMatchedTrack' in string[0]:
            string[1] = bool(string[1])

    # формирование строки запроса
    columns = ','.join([f'"{x[0]}"' for x in data_to_insert])
    param_placeholders = ','.join(['%s' for x in range(len(data_to_insert))])
    query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
    param_values = tuple(x[1] for x in data_to_insert)
    try:
        cur.execute(query, param_values)
    except Exception as e:
        print(f'\r\nException: {e}')
    else:
        print(query, param_values)


def insert_into_bd(data: list, cur: any, table_name: str):
    data_to_insert = []

    # Для того чтобы узнать имена полей таблицы
    cur.execute(f'SELECT * FROM "{table_name}";')
    col_names = []
    for elt in cur.description:
        col_names.append(elt[0])

    for node in data:
        for i in node:
            if type(i) is dict:
                k = list(i.keys())[0]
                if k in col_names:
                    items = [[k, v] for k, v in i.items()][0]
                    data_to_insert.append(items)

        execute(data_to_insert, table_name, cur)
        data_to_insert.clear()
