import psycopg2


def connection() -> any:
    conn = psycopg2.connect(dbname='Telemetry', user='postgres',
                            password='123', host='localhost')
    conn.autocommit = True
    cur = conn.cursor()
    return cur, conn


def insert_data_to_db(table_name: str, cur: any, data: list):
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
        print(f'INSERT INTO "{table_name}" {data}')


def read_data_from_db(table_name: str, cur: any, data: dict) -> any:
    # Для того чтобы узнать имена полей таблицы
    cur.execute(f'SELECT * FROM "{table_name}";')
    col_names = []
    for elt in cur.description:
        col_names.append(elt[0])

    # формирование строки запроса
    columns = ','.join([f'"{x}"' for x in data])
    param_placeholders = ','.join(['%s' for x in range(len(data))])
    query = f'SELECT * FROM "{table_name}" WHERE ({columns}) = ({param_placeholders})'
    param_values = tuple(x for x in data.values())
    # param_values = (3, 1)
    try:
        cur.execute(query, param_values)
    except Exception as e:
        print(f'\r\nException: {e}')
    else:
        db_values = cur.fetchall()
        if db_values:
            wis = dict(zip(col_names, db_values[0]))
            print(wis)
            return wis
        else:
            return None


def prepare_data_for_db(table_name: str, cur: any, data) -> list:
    data_to_insert = []
    # Для того чтобы узнать имена полей таблицы
    cur.execute(f'SELECT * FROM "{table_name}";')
    col_names = []
    for elt in cur.description:
        col_names.append(elt[0])

    # Преобразование типов (int ---> bool), имен ('type' => 'markType')
    if type(data) is list:
        for group in data:
            for k, v in group.items():
                if 'isFake' in k:
                    group['isFake'] = bool(v)
                elif 'type' in k:
                    group['markType'] = group.pop('type')
                    break
                elif 'processingTime' in k:
                    group['scanTime'] = group.pop('processingTime')
                    break
                # elif 'azimuth' in k:
                #     group['beamAzimuth'] = group.pop('azimuth')
                #     break
                # elif 'elevation' in k:
                #     group['beamElevation'] = group.pop('elevation')
                #     break
    else:
        for k, v in data.items():
            # if 'azimuth' in k:
            #     data['epsilonBSK'] = data.pop('azimuth')
            # elif 'elevation' in k:
            #     data['betaBSK'] = data.pop('elevation')
            if 'resolvedDistance' in k:
                data['numDistanceZone'] = data.pop('resolvedDistance')
            elif 'resolvedVelocity' in k:
                data['numVelocityZone'] = data.pop('resolvedVelocity')
            elif 'distancePeriod' in k:
                data['distanceZoneWeight'] = data.pop('distancePeriod')
            elif 'velocityPeriod' in k:
                data['velocityZoneWeight'] = data.pop('velocityPeriod')
            elif 'nextUpdateTimeSeconds' in k:
                data['nextTimeUpdate'] = data.pop('nextUpdateTimeSeconds')

    if type(data) is dict:
        for key, value in data.items():
            if key in col_names:
                data_to_insert.append([key, value])

    elif type(data) is list:
        for i in data:
            for k, v in i.items():
                if k in col_names:
                    data_to_insert.append([k, v])

    return data_to_insert
