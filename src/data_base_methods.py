import psycopg2
import re

# ALTER SEQUENCE "Candidates_Candidate_seq" restart with 1;

# SELECT DISTINCT "taskId", "taskType", "antennaId"
# 	FROM public."BeamTasks"
# 	ORDER BY "taskId";


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


def map_values(data: dict, col_names: list) -> dict:
    z = []
    for k, v in data.items():
        if 'isFake' in k:
            data['isFake'] = bool(v)
            if data['isFake']:
                raise Exception
        # elif 'taskType' in k:
            # data['markType'] = data.pop('taskType')
            # break
        elif 'processingTime' in k:
            data['scanTime'] = data.pop('processingTime')
        # elif 'azimuth' in k:
        #     data['beamAzimuth'] = data.pop('azimuth')
        #     break
        # elif 'elevation' in k:
        #     data['beamElevation'] = data.pop('elevation')
        #     break
        if 'distancePeriod' in k:
            data['distanceZoneWeight'] = data.pop('distancePeriod')
        elif 'velocityPeriod' in k:
            data['velocityZoneWeight'] = data.pop('velocityPeriod')
        elif re.search(r'\bdistance\b', k) and 'distance' not in col_names:
            data['numDistanceZone'] = data.pop('distance')
        elif re.search(r'\bvelocity\b', k):
            data['numVelocityZone'] = data.pop('velocity')
        elif 'possiblePeriod[' in k:
            z.append(v)
            data.clear()
            if len(z) == 6:
                data.append({'possiblePeriods': z})
        elif 'scanPeriodSeconds' in k:
            data['scanPeriod'] = data.pop('scanPeriodSeconds')
        elif 'nextUpdateTimeSeconds' in k:
            data['nextTimeUpdate'] = data.pop('nextUpdateTimeSeconds')

    return data


def prepare_data_for_db(table_name: str, cur: any, data: dict) -> list:
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
