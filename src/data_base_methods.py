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


def read_from_db(table_name: str, cur: any, data: dict) -> any:
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
    try:
        cur.execute(query, param_values)
    except Exception as e:
        print(f'\r\nException: {e}')
    else:
        db_values = cur.fetchall()
        if db_values:
            wis = dict(zip(col_names, db_values[0]))
            # print(wis)
            return wis
        else:
            return None


def map_values(data: list, col_names: list) -> list:
    z = []
    if type(data) is list:
        for group in data:
            for k, v in group.items():
                if 'isFake' in k:
                    group['isFake'] = bool(v)
                    if group['isFake']:
                        raise Exception
                # elif 'taskType' in k:
                    # group['markType'] = group.pop('taskType')
                    # break
                elif 'processingTime' in k:
                    group['scanTime'] = group.pop('processingTime')
                    break
                # elif 'azimuth' in k:
                #     group['beamAzimuth'] = group.pop('azimuth')
                #     break
                # elif 'elevation' in k:
                #     group['beamElevation'] = group.pop('elevation')
                #     break
                if 'distancePeriod' in k:
                    group['distanceZoneWeight'] = group.pop('distancePeriod')
                    break
                elif 'velocityPeriod' in k:
                    group['velocityZoneWeight'] = group.pop('velocityPeriod')
                    break
                elif 'distance' in k and 'distance' not in col_names:
                    group['numDistanceZone'] = group.pop('distance')
                    break
                elif 'velocity' in k:
                    group['numVelocityZone'] = group.pop('velocity')
                    break
                elif 'possiblePeriod[' in k:
                    z.append(v)
                    group.clear()
                    if len(z) == 6:
                        data.append({'possiblePeriods': z})
                        # z.clear()
                    break
                elif 'scanPeriodSeconds' in k:
                    group['scanPeriod'] = group.pop('scanPeriodSeconds')
                    break
                elif 'nextUpdateTimeSeconds' in k:
                    group['nextTimeUpdate'] = group.pop('nextUpdateTimeSeconds')
                    break

    return data


def prepare_data_for_db(table_name: str, cur: any, data) -> list:
    data_to_insert = []
    # Для того чтобы узнать имена полей таблицы
    cur.execute(f'SELECT * FROM "{table_name}";')
    col_names = []
    for elt in cur.description:
        col_names.append(elt[0])

    # MAPPING (int ---> bool), имен ('type' => 'markType')
    data = map_values(data, col_names)

    if type(data) is dict:
        # 2839
        for key, value in data.items():
            if key in col_names:
                data_to_insert.append([key, value])

    elif type(data) is list:
        for i in data:
            for k, v in i.items():
                if k in col_names:
                    data_to_insert.append([k, v])

    return data_to_insert
