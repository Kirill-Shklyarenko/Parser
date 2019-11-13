import psycopg2
import re
import pprint


class DB:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.cur = self.connection()

    def connection(self) -> any:
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        cur = conn.cursor()
        return cur

    def insert_data_to_db(self, table_name: str, z: dict):
        data = [[k, v] for k, v in z.items()]
        # формирование строки запроса
        columns = ','.join([f'"{x[0]}"' for x in data])
        param_placeholders = ','.join(['%s' for x in range(len(data))])
        query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
        param_values = tuple(x[1] for x in data)
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            print(f'\r\nException: {e}')
        else:
            print(f'INSERT INTO "{table_name}" {data}')

    def read_from(self, table_name: str, z: dict, fields: list) -> any:
        data = {}
        for key, value in z.items():
            if key in fields:
                data.update({key: value})

        # Для того чтобы узнать имена полей таблицы
        self.cur.execute(f'SELECT * FROM "{table_name}";')
        col_names = []
        for elt in self.cur.description:
            col_names.append(elt[0])

        # формирование строки запроса
        columns = ','.join([f'"{x}"' for x in data])
        param_placeholders = ','.join(['%s' for x in range(len(data))])
        query = f'SELECT * FROM "{table_name}" WHERE ({columns}) = ({param_placeholders})'
        param_values = tuple(x for x in data.values())
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            print(f'\r\nException: {e}')
        else:
            return None

    @staticmethod
    def map_values(data: dict, col_names: list) -> dict:
        z = []
        returned_data = {}
        for k, v in data.items():
            if 'isFake' in k:
                data['isFake'] = bool(v)
                if data['isFake']:
                    raise Exception
            elif 'processingTime' in k:
                returned_data['scanTime'] = data['processingTime']
            elif 'distancePeriod' in k:
                returned_data['distanceZoneWeight'] = data['distancePeriod']
            elif 'velocityPeriod' in k:
                returned_data['velocityZoneWeight'] = data['velocityPeriod']
            elif 'beamAzimuth' in k and 'beamAzimuth' not in col_names:
                returned_data['betaBSK'] = data['beamAzimuth']
            elif 'beamElevation' in k and 'beamElevation' not in col_names:
                returned_data['epsilonBSK'] = data['beamElevation']
            elif 'type' in k and 'type' not in col_names:
                returned_data['markType'] = data['type']
            elif re.search(r'\bdistance\b', k) and 'distance' not in col_names:
                returned_data['numDistanceZone'] = data['resolvedDistance']
            elif re.search(r'\bvelocity\b', k):
                returned_data['numVelocityZone'] = data['resolvedVelocity']
            elif 'possiblePeriod[' in k:
                z.append(v)
            elif 'scanPeriodSeconds' in k:
                returned_data['scanPeriod'] = data['scanPeriodSeconds']
            elif 'nextUpdateTimeSeconds' in k:
                returned_data['nextTimeUpdate'] = data['nextUpdateTimeSeconds']
            elif 'creationTimeSeconds' in k:
                returned_data['nextTimeUpdate'] = data['creationTimeSeconds']

        if len(z) == 6:
            returned_data.update({'possiblePeriods': z})
        returned_data.update(data)
        return returned_data

    def prepare_data_for_db(self, table_name: str, cur: any, data: dict) -> dict:
        data_to_insert = {}
        # Узнаем имена полей таблицы
        cur.execute(f'SELECT * FROM "{table_name}";')
        col_names = []
        for elt in cur.description:
            col_names.append(elt[0])

        # MAPPING (int ---> bool), имен ('type' => 'markType')
        data = self.map_values(data, col_names)

        for key, value in data.items():
            if key in col_names:
                data_to_insert.update({key: value})

        db_values = self.cur.fetchall()
        if db_values:
            wis = dict(zip(col_names, db_values[0]))
            return wis
        else:
            return None


