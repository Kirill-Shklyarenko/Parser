import psycopg2
import logging as log


class DataBase:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.cur = self.connection()

    def connection(self) -> any:
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        cur = conn.cursor()
        return cur

    def insert_to(self, table_name: str, dict_to_insert: dict):
        # Для того чтобы узнать имена полей таблицы
        self.cur.execute(f'SELECT * FROM "{table_name}";')
        col_names = []
        for elt in self.cur.description:
            col_names.append(elt[0])
        data = [[k, v] for k, v in dict_to_insert.items() if k in col_names]
        # формирование строки запроса
        columns = ','.join([f'"{x[0]}"' for x in data])
        param_placeholders = ','.join(['%s' for x in range(len(data))])
        query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
        param_values = tuple(x[1] for x in data)
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            log.exception(f'\r\nException: {e}')
        else:
            log.warning(f'INSERT INTO "{table_name}" {data}')

    def read_from(self, table_name: str, dict_for_get_pk: dict) -> any:
        data = {}
        # data.update({key: value for key, value in z.items() if key in fields})
        # формирование строки запроса
        columns = ','.join([f'"{x}"' for x in dict_for_get_pk])
        param_placeholders = ','.join(['%s' for x in range(len(dict_for_get_pk))])
        query = f'SELECT * FROM "{table_name}" WHERE ({columns}) = ({param_placeholders})'
        param_values = tuple(x for x in dict_for_get_pk.values())
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            log.exception(f'\r\nException: {e}')
        else:
            db_values = self.cur.fetchall()
            if db_values:
                return db_values[0]
            else:
                return None

    def get_pk(self, table_name: str, pk_name: str, dict_for_get_pk: dict):
        # columns_names = []
        # data = {}
        # pk_name = ''
        # if table_name is 'BeamTasks':
            # columns_names = ["taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
            #                  "threshold", "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
            #                  "upperDistanceTrim", "beamAzimuth", "beamElevation"]
            # pk_name = 'BeamTask'
        # elif table_name is 'PrimaryMarks':
            # columns_names = ["BeamTask", "PrimaryMark", "primaryMarkId", "scanTime", "azimuth", "elevation",
            #                  "markType", "distance", "dopplerSpeed", "signalLevel", "reflectedEnergy",
            #                  "antennaId", "taskType", "beamAzimuth", "beamElevation"]
            # pk_name = 'PrimaryMark'
        # data.update({key: value for key, value in z.items() if key in columns_names})
        data_with_pk = self.read_from(table_name, dict_for_get_pk)
        if data_with_pk:
            # log.debug(f'{pk_name} : {data_with_pk[0]}')
            # dict_for_get_pk.update({pk_name: data_with_pk[0]})
            return {pk_name: data_with_pk[0]}
        else:
            log.debug(f'get_pk data is None')
            return None
