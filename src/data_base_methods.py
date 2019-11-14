import psycopg2
import re
import pprint


class DataBase:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.cur = self.connection()

    def connection(self) -> any:
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        cur = conn.cursor()
        return cur

    def insert_to(self, table_name: str, z: dict):
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
            pprint.pprint(f'INSERT INTO "{table_name}" {data}')

    def read_from(self, table_name: str, z: dict, fields: list) -> any:
        data = {}
        data.update({key: value for key, value in z.items() if key in fields})
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
            db_values = self.cur.fetchall()
            if db_values:
                # wis = dict(zip(col_names, db_values[0]))
                return db_values[0]
            else:
                return None


class FrameHandler(DataBase):
    def __init__(self, frame, dsn: str):
        super().__init__(dsn)
        self.frame = frame
        self.task = {}

    @staticmethod
    def map_values(data: dict) -> dict:
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
            elif 'betaBSK' in k:
                returned_data['beamAzimuth'] = data['betaBSK']
            elif 'epsilonBSK' in k:
                returned_data['beamElevation'] = data['epsilonBSK']
            elif 'type' in k:
                returned_data['markType'] = data['type']
            elif re.search(r'\bdistance\b', k):
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

    def beam_task(self):
        for index, group in enumerate(self.frame):
            if re.search(r'\bTask\b', group[0]):
                group.pop(0)
                for c in group:
                    self.task.update(c)

            elif re.search(r'beamTask', group[0]):
                group.pop(0)
                beam_task = {}
                beam_task.update(self.task)
                for c in group:
                    beam_task.update(c)

                print('Task_type == ', beam_task['taskType'])
                self.frame = self.frame[index + 1:]
                beam_task = self.map_values(beam_task)
                return beam_task

    def get_pk(self, table_name: str, z: dict, columns_for_get_pk: list):
        columns_names = ["taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
                         "threshold", "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
                         "upperDistanceTrim", "beamAzimuth", "beamElevation"]
        data = {}
        data.update({key: value for key, value in z.items() if key in columns_names})
        bt_data = DataBase.read_from(self, table_name, data, columns_for_get_pk)
        if bt_data:
            data.update({'BeamTask': bt_data[0]})
            return data
        else:
            return None

# def beamtask_columns(func):
#     def wrapper(*args, **kwargs):
#         columns_names = ["taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
#                          "threshold", "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
#                          "upperDistanceTrim", "beamAzimuth", "beamElevation"]
#
#         print ("Передали ли мне что-нибудь?:")
#         print (args)
#         print (kwargs)      # Теперь мы распакуем *args и **kwargs
#         func(*args, **kwargs)
#         print(func)
#     return wrapper
