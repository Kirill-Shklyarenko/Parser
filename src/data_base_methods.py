import logging.config
import textwrap

import psycopg2

from decorators import pk

log = logging.getLogger('simpleExample')


class DataBaseMain:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.cur = self.connection()

    def connection(self) -> any:
        conn = None
        try:
            conn = psycopg2.connect(self.dsn)
        except Exception as e:
            log.exception(f'{e}')
            # print(f'Do you want restore DataBase?')
            # print(f'y/n')
            # i = input()
            # if i == 'y':
            # self.data_base_restore()
        conn.autocommit = True
        cur = conn.cursor()
        log.info(f'DataBase connection complete')
        return cur

    def insert_to_table(self, table_name: str, data: dict):
        columns = ','.join([f'"{x}"' for x in data])
        param_placeholders = ','.join(['%s' for x in range(len(data))])
        query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
        param_values = tuple(x for x in data.values())
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            log.exception(f'\r\nException: {e}')
        finally:
            log.warning(textwrap.fill(f'INSERT INTO "{table_name}" {data}', 100,
                                      subsequent_indent='                                      '))

    def read_from_table(self, table_name: str, dict_for_get_pk: dict) -> int:
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

    def rename_table_column(self, table_name: str, data: dict):
        k, v = data.items()
        query = f'ALTER TABLE "{table_name}" RENAME {k} TO {v}'
        try:
            self.cur.execute(query)
        except Exception as e:
            log.exception(f'\r\nException: {e}')


class DataBase(DataBaseMain):
    def __init__(self, dsn: str):
        super().__init__(dsn)

    def get_pk(self, table_name: str, dict_for_get_pk: dict) -> int:
        data_with_pk = self.read_from_table(table_name, dict_for_get_pk)
        if data_with_pk:
            log.debug(f'succsessfull get primary key : {data_with_pk[0]}')
            return data_with_pk[0]
        else:
            log.warning(f'In {table_name} : PK : doesnt exists : {dict_for_get_pk}')

    def map_bin_fields_to_table(self, table_name: str, data: dict) -> dict:
        # Для того чтобы узнать имена полей таблицы
        self.cur.execute(f'SELECT * FROM "{table_name}"')
        col_names = []
        for elt in self.cur.description:
            col_names.append(elt[0])
        data = {k: v for k, v in data.items() if k in col_names}
        return data

    def get_pk_for_BTs(self, full_block_dict: dict):
        table_name = 'BeamTasks'
        result = {}
        if 'state' in full_block_dict:                         # блок = Candidate
            fields_for_get_pk = ['taskId', 'antennaId']
            result.update({'taskType': 2})
            for k, v in full_block_dict.items():
                if k in fields_for_get_pk:
                    result.update({k:v})
                if k == 'id':
                    result.update({'trackId': v})

        elif 'type' in full_block_dict:                        # блок = AirTracksHistory
            fields_for_get_pk = ['antennaId']
            result.update({'taskType': 3})
            for k, v in full_block_dict.items():
                if k in fields_for_get_pk:
                    result.update({k:v})
                if k == 'id':
                    result.update({'trackId': v})

        else:                                                  # блок = BeamTask & PrimaryMark
            fields_for_get_pk = ['taskId', 'antennaId']
            for k, v in full_block_dict.items():
                if k in fields_for_get_pk:
                    result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_PMs(self, full_block_dict: dict):
        table_name = 'PrimaryMarks'
        fields_for_get_pk = ['BeamTask']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_Cs(self, full_block_dict: dict):
        table_name = 'Candidates'
        fields_for_get_pk = ['id']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_As(self, full_block_dict: dict):
        table_name = 'AirTracks'
        fields_for_get_pk = ['id']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_CHs(self, full_block_dict: dict):
        table_name = 'CandidatesHistory'
        fields_for_get_pk = ['BeamTask', 'PrimaryMark']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_AHs(self, full_block_dict: dict):
        table_name = 'AirTracksHistory'
        fields_for_get_pk = ['AirTracksHistory', 'PrimaryMark', 'CandidateHistory']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_Fs(self, full_block_dict: dict):
        table_name = 'ForbiddenSectors'
        fields_for_get_pk = ['azimuthBeginNSSK', 'azimuthEndNSSK','elevationBeginNSSK','elevationEndNSSK']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk


