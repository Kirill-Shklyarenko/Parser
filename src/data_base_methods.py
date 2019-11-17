import logging as log

import psycopg2


class DataBase:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.cur = self.connection()

    def connection(self) -> any:
        conn = None
        try:
            conn = psycopg2.connect(self.dsn)
        except Exception as e:
            log.exception(f'{e}')
            return None
        finally:
            conn.autocommit = True
            cur = conn.cursor()
            log.debug(f'DataBase connection complete')
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
            log.warning(f'INSERT INTO "{table_name}" {data}\r')

    def read_from_table(self, table_name: str, dict_for_get_pk: dict) -> any:
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

    def get_pk(self, table_name: str, pk_name: str, dict_for_get_pk: dict) -> any:
        data_with_pk = self.read_from_table(table_name, dict_for_get_pk)
        if data_with_pk:
            log.debug(f'{pk_name} : {data_with_pk[0]}')
            dict_for_get_pk.update({pk_name: data_with_pk[0]})
            return {pk_name: data_with_pk[0]}
        else:
            log.debug(f'{table_name} : {dict_for_get_pk} doesnt exists')
            return None

    def map_bin_fields_to_table(self, table_name: str, data: dict) -> dict:
        # Для того чтобы узнать имена полей таблицы
        self.cur.execute(f'SELECT * FROM "{table_name}";')
        col_names = []
        for elt in self.cur.description:
            col_names.append(elt[0])
        data = {k: v for k, v in data.items() if k in col_names}
        return data

    @staticmethod
    def map_table_fields_to_table(dict_from_telemetry: dict, formatter_dict: dict) -> dict:
        result = {}
        for fk, fv in dict_from_telemetry.items():
            if 'isFake' in fk:
                dict_from_telemetry[fk] = bool(dict_from_telemetry[fk])
            for sk, sv in formatter_dict.items():
                if fk == sv:
                    result.update({sk: fv})
        formatter_dict.update(result)
        return formatter_dict

    # def nullify_the_sequences(self, table_name: str, seq_name: str):
    #     query = f'ALTER SEQUENCE "{table_name}_{seq_name}_seq" restart with 1'
    #     try:
    #         self.cur.execute(query)
    #     except Exception as e:
    #         log.exception(f'\r\nException: {e}')
    #     finally:
    #         log.warning(f'ALTER SEQUENCE "{table_name}_{seq_name}_seq" restart with 1')
