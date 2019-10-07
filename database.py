import psycopg2

with psycopg2.connect(dbname='telemetry', user='postgres',
                      password='123', host='localhost') as conn:
    with conn.cursor as cur:
        cur.execute("SELECT * FROM air_track_periods")
        res = cur.fetchall()
        print(res)
