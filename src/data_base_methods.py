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

    def insert_to(self, table_name: str, data: dict):
        # формирование строки запроса
        columns = ','.join([f'"{x}"' for x in data])
        param_placeholders = ','.join(['%s' for x in range(len(data))])
        query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
        param_values = tuple(x for x in data.values())
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
        data_with_pk = self.read_from(table_name, dict_for_get_pk)
        if data_with_pk:
            log.debug(f'{pk_name} : {data_with_pk[0]}')
            dict_for_get_pk.update({pk_name: data_with_pk[0]})
            return {pk_name: data_with_pk[0]}
        else:
            log.debug(f'{table_name} : {dict_for_get_pk} doesnt exists')
            return None

    def map_fields_bin_to_table(self, table_name: str, data: dict) -> dict:
        # Для того чтобы узнать имена полей таблицы
        self.cur.execute(f'SELECT * FROM "{table_name}";')
        col_names = []
        for elt in self.cur.description:
            col_names.append(elt[0])
        data = {k: v for k, v in data.items() if k in col_names}
        return data
