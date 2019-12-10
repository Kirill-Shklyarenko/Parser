import logging.config
import os
import textwrap
from pathlib import Path
from subprocess import Popen, PIPE

import psycopg2

log = logging.getLogger('simpleExample')


class DataBaseMain:
    __slots__ = ('__dsn', 'cur')

    def __init__(self):
        self.__dsn = self.__dsn_string()
        self.cur = self.connection()

    @staticmethod
    def __dsn_string():
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

    def connection(self):
        try:
            conn = psycopg2.connect(dbname=self.__dsn['dbname'], user=self.__dsn['user'],
                                    host=self.__dsn['host'], password=self.__dsn['password'], port=5432)

        except psycopg2.OperationalError:
            log.info(textwrap.fill(f'There is no existing DataBase. Do You want to create new and RESTORE'
                                   f' from backup file?', 80,
                                   subsequent_indent='                   '))
            log.info(f'INPUT "y" if YES or press ENTER')
            answer = input()
            if answer == 'y':
                DataBaseCreator(self.__dsn)
                conn = psycopg2.connect(dbname=self.__dsn['dbname'], user=self.__dsn['user'],
                                        host=self.__dsn['host'], password=self.__dsn['password'], port=5432)
            else:
                exit()
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
            log.exception(f'\r\nException: {e}')
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
            log.exception(f'\r\nException: {e}')
        else:
            db_values = self.cur.fetchall()
            return db_values

    def update_tables(self, table_name: str, update_dict: dict, where_condition: dict):
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
            log.exception(f'\r\nException: {e}')
        finally:
            log.warning(textwrap.fill(f'{self.cur.query}', 80,
                                      subsequent_indent='                   '))


class DataBase(DataBaseMain):
    def __init__(self):
        super().__init__()

    def get_pk(self, table_name: str, where_condition: dict) -> int:
        data_with_pk = self.read_from_table(table_name, where_condition)
        if data_with_pk:
            log.debug(f'PK from {table_name} received successfully : {data_with_pk[0][0]}')
            return data_with_pk[0][0]
        else:
            log.warning(f'PK in {table_name} : doesnt exists : {where_condition}')

    def read_specific_field(self, table_name: str, specific_field_name: str, where_condition: dict) -> dict:
        data_with_pk = self.read_from_table(table_name, where_condition)
        for idx, col in enumerate(self.cur.description):
            if [col[0]][0] == specific_field_name:
                log.debug(
                    f'"{specific_field_name}" from {table_name} received : {data_with_pk[0][idx]}')
                return {specific_field_name: data_with_pk[0][idx]}

    # - FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN ---FIN- #
    # - FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN ---FIN- #
    # - FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN ---FIN- #

    def get_pk_beam_tasks(self, dict_for_get_pk: dict) -> int:
        table_name = 'BeamTasks'
        return self.get_pk(table_name, dict_for_get_pk)

    def get_pk_primary_marks(self, dict_for_get_pk: dict) -> int:
        table_name = 'PrimaryMarks'
        return self.get_pk(table_name, dict_for_get_pk)

    def get_pk_candidates(self, ids: int) -> int:
        table_name = 'Candidates'
        return self.get_pk(table_name, {'id': ids})

    def get_pk_cand_hists(self, dict_for_get_pk: dict) -> int:
        table_name = 'CandidatesHistory'
        return self.get_pk(table_name, dict_for_get_pk)

    def get_pk_air_tracks(self, ids: int) -> int:
        table_name = 'AirTracks'
        return self.get_pk(table_name, {'id': ids})

    def get_pk_tracks_hists(self, dict_for_get_pk: dict) -> int:
        table_name = 'AirTracksHistory'
        return self.get_pk(table_name, dict_for_get_pk)

    def get_pk_forb_sectors(self, az_b_nssk: float, az_e_nssk: float, elev_b_nssk: float, elev_e_nssk: float) -> int:
        table_name = 'ForbiddenSectors'
        return self.get_pk(table_name, {'azimuthBeginNSSK': az_b_nssk, 'azimuthEndNSSK': az_e_nssk,
                                        'elevationBeginNSSK': elev_b_nssk, 'elevationEndNSSK': elev_e_nssk})


class DataBaseCreator:
    def __init__(self, dsn):
        self.__dsn = dsn
        self.cur = self.__create_data_base()
        self.__check_conf_file()

        self.__restore_data_base()

    def __check_conf_file(self):
        app_data = os.environ.copy()["APPDATA"]
        postgres_path = Path(f'{app_data}\postgresql')
        __pgpass_file = Path(f'{postgres_path}\pgpass.conf')
        try:
            os.makedirs(postgres_path)
        except Exception as _:
            f'{_}'
        finally:
            if os.path.isfile(__pgpass_file):
                log.debug(f'File "pgpass.conf" already exists')
                with open(__pgpass_file, 'r+') as f:
                    content = f.readlines()
                    if f'{self.__dsn["host"]}:{5432}:{self.__dsn["dbname"]}:' \
                       f'{self.__dsn["user"]}:{int(self.__dsn["password"])}\n' \
                       f'{self.__dsn["host"]}:{5432}:{self.__dsn["dbname"]}:' \
                       f'{os.environ["UserName"]}:{int(self.__dsn["password"])}\n' not in content:
                        # сервер: порт:база_данных: имя_пользователя:пароль
                        f.write(f'{self.__dsn["host"]}:{5432}:{self.__dsn["dbname"]}:'
                                f'{self.__dsn["user"]}:{int(self.__dsn["password"])}\n'
                                f'{self.__dsn["host"]}:{5432}:{self.__dsn["dbname"]}:'
                                f'{os.environ["UserName"]}:{int(self.__dsn["password"])}\n')
                    else:
                        log.info(f'{self.__dsn["host"]}:5432:{self.__dsn["dbname"]}:'
                                 f'{self.__dsn["user"]}:{self.__dsn["password"]}'
                                 f' already in "pgpass.conf" file')
            else:
                log.debug(f'File "pgpass.conf" not exists')
                with open(__pgpass_file, 'x') as f:
                    # сервер: порт:база_данных: имя_пользователя:пароль
                    f.write(f'{self.__dsn["host"]}:5432:{self.__dsn["dbname"]}:'
                            f'{self.__dsn["user"]}:{self.__dsn["password"]}\n')

    def __create_data_base(self):
        try:
            conn = psycopg2.connect(dbname='postgres', user=self.__dsn['user'],
                                    host=self.__dsn['host'], password=self.__dsn['password'], port=5432)
        except Exception as _:
            log.exception(f'{_}')
        else:
            conn.autocommit = True
            cur = conn.cursor()
            query = f'CREATE DATABASE "{self.__dsn["dbname"]}"'
            cur.execute(query)
            return cur

    def __restore_data_base(self):
        col = [x for x in self.__dsn.values()]
        folder_name = Path(__file__).parent.parent
        folder_name_data = os.path.join(folder_name, 'data')
        file_to_open = os.path.join(folder_name_data, 'bd.backup')
        cmd = f'pg_restore --host={col[3]} --dbname={col[0]} --username={col[1]} ' \
              f'--verbose=True --no-password {file_to_open}'
        try:
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        except FileNotFoundError:
            log.info(f'FileNotFoundError: [WinError 2] Не удается найти указанный файл')
            log.info(textwrap.fill(f'You need to SET Windows $PATH for use "pg_restore" in cmd', 80,
                                   subsequent_indent='                   '))
        else:
            stderr = proc.communicate()[1].decode('utf-8', errors="ignore").strip()
            print(stderr)
