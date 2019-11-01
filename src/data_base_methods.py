import psycopg2


def connection() -> any:
    conn = psycopg2.connect(dbname='telemetry', user='postgres',
                            password='123', host='localhost')
    conn.autocommit = True
    cur = conn.cursor()
    return cur, conn


def insert_into(table_name: str, data: list, cur: any):
    # формирование строки запроса
    columns = ','.join([f'"{x[0]}"' for x in data])
    param_placeholders = ','.join(['%s' for x in range(len(data))])
    query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
    param_values = tuple(x[1] for x in data)
    try:
        cur.execute(query, param_values)
    except Exception as e:
        print(f'\r\nException: {e}')
    else:
        print(query, param_values)


def map_values(data):
    # Преобразование типов (int ---> bool)
    for group in data:
        if 'isFake' in group[0]:
            group[1] = bool(group[1])
        if 'hasMatchedTrack' in group[0]:
            group[1] = bool(group[1])


def prepare_data(table_name: str, data: list, cur: any):
    data_to_insert = []
    col_names = []
    # Для того чтобы узнать имена полей таблицы
    cur.execute(f'SELECT * FROM "{table_name}";')
    for elt in cur.description:
        col_names.append(elt[0])

    for group in data:
        for i in group:
            if type(i) is dict:
                k = list(i.keys())[0]
                if k in col_names:
                    items = [[k, v] for k, v in i.items()][0]
                    data_to_insert.append(items)

        map_values(data_to_insert)
        insert_into(table_name, data_to_insert, cur)
        data_to_insert.clear()
