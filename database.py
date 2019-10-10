import psycopg2


def db_insert(info):
    with psycopg2.connect(dbname='telemetry', user='postgres',
                          password='123', host='localhost') as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "insert into %s values (%%s, %%s)" % info.get('block_name'),
                    [info.get('variable_name'), info.get('value')]
                    )
            except Exception as e:
                print(e)
