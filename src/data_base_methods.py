import logging.config
import os
import textwrap
from pathlib import Path
from subprocess import Popen, PIPE

import psycopg2

log = logging.getLogger('simpleExample')


class DataBaseAPI:
    __slots__ = ('__dsn', 'cur')

    def __init__(self):
        self.__dsn = self.__dsn_string()
        self.cur = self.__connection()

    @staticmethod
    def __dsn_string() -> dict:
        log.info(f'INPUT name of DataBase')
        name = input()
        log.info(f'INPUT password of DataBase')
        password = input()
        log.info(f'INPUT user_name of DataBase or press ENTER if user_name="postgres"')
        user_name = input()
        if len(user_name) == 0:
            user_name = 'postgres'
        log.info(f'INPUT host_name of DataBase or press ENTER if host_name="localhost"')
        host_name = input()
        if len(host_name) == 0:
            host_name = 'localhost'
        return {'dbname': name, 'user': user_name, 'password': password, 'host': host_name}

    def __connection(self):
        try:
            conn = psycopg2.connect(dbname=self.__dsn['dbname'], user=self.__dsn['user'],
                                    host=self.__dsn['host'], password=self.__dsn['password'], port=5432)
        except psycopg2.OperationalError:
            log.info(textwrap.fill(f'There is no existing DataBase. Creating new DataBase', 80,
                                   subsequent_indent='                   '))
            DataBaseCreator(self.__dsn)
            conn = psycopg2.connect(dbname=self.__dsn['dbname'], user=self.__dsn['user'],
                                    host=self.__dsn['host'], password=self.__dsn['password'], port=5432)
        finally:
            conn.autocommit = True
            cur = conn.cursor()
            log.info(f'DataBase connection complete')
            return cur

    def insert_to_table(self, table_name: str, data: dict):
        columns = ','.join([f'"{x}"' for x in data])
        param_placeholders = ','.join(['%s' for _ in range(len(data))])
        query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
        param_values = tuple(x for x in data.values())
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            log.exception(f'\nException: {e}')
        else:
            log.warning(textwrap.fill(f'INSERT INTO "{table_name}" {data}', 80,
                                      subsequent_indent='                   '))

    def read_from_table(self, table_name: str, where_condition: dict) -> list:
        columns = ','.join([f'"{x}"' for x in where_condition])
        param_placeholders = ','.join(['%s' for _ in range(len(where_condition))])
        query = f'SELECT * FROM "{table_name}" WHERE ({columns}) = ({param_placeholders})'
        param_values = tuple(x for x in where_condition.values())
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            log.exception(f'\nException: {e}')
        else:
            db_values = self.cur.fetchall()
            return db_values

    def update_table(self, table_name: str, update_dict: dict, where_condition: dict):
        where_condition_keys = [x for x in where_condition.keys()]
        for x in where_condition_keys:
            del update_dict[x]
        columns = ','.join([f'"{x}"' for x in update_dict])
        param_placeholders = ','.join(['%s' for _ in range(len(update_dict))])
        keys = ' and '.join([f'"{k}" = {v}' for k, v in where_condition.items()])
        query = f'UPDATE "{table_name}" SET ({columns}) = ({param_placeholders})' \
                f'WHERE {keys}'
        params_values = tuple(x for x in update_dict.values())
        try:
            self.cur.execute(query, params_values)
        except Exception as e:
            log.exception(f'\nException: {e}')
        finally:
            log.warning(textwrap.fill(f'UPDATE {table_name} SET {update_dict} WHERE {where_condition}', 85,
                                      subsequent_indent='                   '))

    def get_pk(self, table_name: str, where_condition: dict) -> int:
        data_with_pk = self.read_from_table(table_name, where_condition)
        if data_with_pk:
            log.debug(f'PK from {table_name} received successfully : {data_with_pk[0][0]}')
            return data_with_pk[0][0]
        else:
            log.warning(textwrap.fill(f'PK in {table_name} : doesnt exists : {where_condition}', 85,
                                      subsequent_indent='                   '))

    def read_specific_field(self, table_name: str, get_field: str, where_condition: dict) -> dict:
        data_with_pk = self.read_from_table(table_name, where_condition)
        for idx, col in enumerate(self.cur.description):
            if [col[0]][0] == get_field:
                log.debug(
                    f'"{get_field}" from {table_name} received : {data_with_pk[0][idx]}')
                return {get_field: data_with_pk[0][idx]}


class DataBase(DataBaseAPI):
    def __init__(self):
        super().__init__()

    def get_pk_candidates(self, ids: int) -> int:
        table_name = 'Candidates'
        return self.get_pk(table_name, {'id': ids})

    def get_pk_air_tracks(self, ids: int) -> int:
        table_name = 'AirTracks'
        return self.get_pk(table_name, {'id': ids})

    def get_pk_beam_tasks(self, dict_for_get_pk: dict) -> int:
        table_name = 'BeamTasks'
        return self.get_pk(table_name, dict_for_get_pk)

    def get_pk_primary_marks(self, dict_for_get_pk: dict) -> int:
        table_name = 'PrimaryMarks'
        return self.get_pk(table_name, dict_for_get_pk)

    def get_pk_cand_hists(self, dict_for_get_pk: dict) -> int:
        table_name = 'CandidatesHistory'
        return self.get_pk(table_name, dict_for_get_pk)

    def get_pk_tracks_hists(self, dict_for_get_pk: dict) -> int:
        table_name = 'AirTracksHistory'
        return self.get_pk(table_name, dict_for_get_pk)

    def get_pk_forb_sectors(self, dict_for_get_pk: dict) -> int:
        table_name = 'ForbiddenSectors'
        return self.get_pk(table_name, dict_for_get_pk)

    #
    #
    def insert_beam_tasks(self, insert_dict: dict):
        table_name = 'BeamTasks'
        fields = ['taskId', 'isFake', 'trackId', 'taskType', 'viewDirectionId', 'antennaId', 'pulsePeriod',
                  'threshold', 'lowerVelocityTrim', 'upperVelocityTrim', 'lowerDistanceTrim',
                  'upperDistanceTrim', 'beamAzimuth', 'beamElevation']
        dict_to_insert = {k: v for k, v in insert_dict.items() if k in fields}
        self.insert_to_table(table_name, dict_to_insert)

    def insert_prim_marks(self, insert_dict: dict):
        table_name = 'PrimaryMarks'
        fields = ["BeamTask", "primaryMarkId", "scanTime", "antennaId", "beamAzimuth", "beamElevation",
                  "azimuth", "elevation", "markType", "distance", "dopplerSpeed", "signalLevel",
                  "reflectedEnergy"]
        dict_to_insert = {k: v for k, v in insert_dict.items() if k in fields}
        self.insert_to_table(table_name, dict_to_insert)

    def insert_candidates(self, insert_dict: dict):
        table_name = 'Candidates'
        fields = ['id']
        dict_to_insert = {k: v for k, v in insert_dict.items() if k in fields}
        self.insert_to_table(table_name, dict_to_insert)

    def insert_cand_histories(self, insert_dict: dict):
        table_name = 'CandidatesHistory'
        fields = ["BeamTask", "PrimaryMark", "Candidate", "azimuth", "elevation", "state", "antennaId",
                  "distanceZoneWidth", "velocityZoneWidth", "numDistanceZone", "numVelocityZone", "timeUpdated"]
        dict_to_insert = {k: v for k, v in insert_dict.items() if k in fields}
        self.insert_to_table(table_name, dict_to_insert)

    def insert_air_tracks(self, insert_dict: dict):
        table_name = 'AirTracks'
        fields = ['id']
        dict_to_insert = {k: v for k, v in insert_dict.items() if k in fields}
        self.insert_to_table(table_name, dict_to_insert)

    def insert_air_tracks_histories(self, insert_dict: dict):
        table_name = 'AirTracksHistory'
        fields = ["CandidatesHistory", "PrimaryMark", "AirTrack", "antennaId"]
        dict_to_insert = {k: v for k, v in insert_dict.items() if k in fields}
        self.insert_to_table(table_name, dict_to_insert)

    #
    #
    def update_air_tracks_histories(self, insert_dict: dict):
        table_name = 'AirTracksHistory'
        fields = ["AirTracksHistory", "AirTrack", "type", "priority", "antennaId", "azimuth", "elevation",
                  "distance", "scanTime", "scanPeriod", "pulsePeriod", "missesCount", "possiblePeriods", "timeUpdated",
                  "sigmaAzimuth", "sigmaElevation", "sigmaDistance", "sigmaRadialVelocity", "radialVelocity",
                  "minRadialVelocity", "maxRadialVelocity", "minDistance", "maxDistance", ]
        update_dict = {k: v for k, v in insert_dict.items() if k in fields}
        where_fields = ['AirTracksHistory', 'AirTrack', 'antennaId']
        where_dict = {k: v for k, v in insert_dict.items() if k in where_fields}
        self.update_table(table_name, update_dict, where_dict)

    def update_candidate_histories(self, insert_dict: dict):
        table_name = 'CandidatesHistory'
        fields = ["BeamTask", "PrimaryMark", "Candidate", "CandidatesHistory"]
        update_dict = {k: v for k, v in insert_dict.items() if k in fields}
        where_fields = ['CandidatesHistory']
        where_dict = {k: v for k, v in insert_dict.items() if k in where_fields}
        self.update_table(table_name, update_dict, where_dict)


class DataBaseCreator:
    def __init__(self, __dsn):
        self.__dsn = __dsn
        self.__check_conf_file()
        self.__create_data_base()
        self.__restore_data_base()

    def __check_conf_file(self):
        __app_data = os.environ.copy()["APPDATA"]
        __postgres_path = Path(f'{__app_data}\postgresql')
        __pgpass_file = Path(f'{__postgres_path}\pgpass.conf')
        parameters = f'{self.__dsn["host"]}:{5432}:{self.__dsn["dbname"]}:' \
                     f'{self.__dsn["user"]}:{int(self.__dsn["password"])}\n'
        if not os.path.isdir(__postgres_path):
            os.makedirs(__postgres_path)
        if os.path.isfile(__pgpass_file):
            log.debug(f'File "pgpass.conf" already exists')
            with open(__pgpass_file, 'r+') as f:
                content = f.readlines()
                if parameters not in content:
                    # сервер: порт:база_данных: имя_пользователя:пароль
                    f.write(parameters)
                else:
                    log.info(f' {parameters} already in "pgpass.conf" file')
        else:
            log.debug(f'File "pgpass.conf" not exists')
            with open(__pgpass_file, 'x') as f:
                # сервер: порт:база_данных: имя_пользователя:пароль
                f.write(parameters)

    def __create_data_base(self):
        try:
            __conn = psycopg2.connect(dbname='postgres', user=self.__dsn['user'],
                                      host=self.__dsn['host'], password=self.__dsn['password'], port=5432)
        except Exception as _:
            log.exception(f'{_}')
        else:
            __conn.autocommit = True
            __cur = __conn.cursor()
            __query = f'CREATE DATABASE "{self.__dsn["dbname"]}"'
            __cur.execute(__query)
            log.info(f'{__query}')

    def __restore_data_base(self):
        __col = [x for x in self.__dsn.values()]
        __folder_name = Path(__file__).parent.parent
        __folder_name_data = os.path.join(__folder_name, 'data')
        __file_to_open = os.path.join(__folder_name_data, 'bd.backup')
        __cmd = f'pg_restore --host={__col[3]} --dbname={__col[0]} --username={__col[1]} ' \
                f'--verbose=True --no-password ' \
                f'{__file_to_open}'
        try:
            __proc = Popen(__cmd, stdout=PIPE, stderr=PIPE)
        except FileNotFoundError:
            log.info(f'FileNotFoundError: [WinError 2] Не удается найти указанный файл')
            log.info(textwrap.fill(f'You need to SET Windows $PATH for use "pg_restore" in cmd', 80,
                                   subsequent_indent='                   '))
        else:
            __stderr = __proc.communicate()[1].decode('utf-8', errors="ignore").strip()
            log.debug(textwrap.fill(f'{__stderr}', 80))
