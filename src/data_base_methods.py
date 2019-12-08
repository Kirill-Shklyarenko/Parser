import logging.config
import textwrap

import psycopg2

log = logging.getLogger('simpleExample')


class DataBaseMain:
    __slots__ = ('dsn', 'cur')

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.cur = self.connection()

    def connection(self):
        conn = None
        try:
            conn = psycopg2.connect(self.dsn)
        except Exception as e:
            print(f'There is no existing DataBase{e}')
            print(f'Do you want to create new DataBase?')
            print(f'y/n')
            i = input()
            if i == 'y':
                d = DataBaseCreator()
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
            log.warning(textwrap.fill(f'INSERT INTO "{table_name}" {data}', 115,
                                      subsequent_indent='                                '))

    def read_from_table(self, table_name: str, where_condition: dict) -> list:
        columns = ','.join([f'"{x}"' for x in where_condition])
        param_placeholders = ','.join(['%s' for x in range(len(where_condition))])
        query = f'SELECT * FROM "{table_name}" WHERE ({columns}) = ({param_placeholders})'
        param_values = tuple(x for x in where_condition.values())
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            log.exception(f'\r\nException: {e}')
        else:
            db_values = self.cur.fetchall()
            if db_values:
                return db_values

    def update_tables(self, table_name: str, update_dict: dict, where_condition: dict):
        columns = ','.join([f'"{x}"' for x in update_dict])
        param_placeholders = ','.join(['%s' for x in range(len(update_dict))])
        keys = '\r and '.join([f'"{k}" = {v}' for k, v in where_condition.items()])
        query = f'UPDATE "{table_name}" SET ({columns}) = ({param_placeholders})' \
                f'WHERE {keys}'
        params_values = tuple(x for x in update_dict.values())
        try:
            self.cur.execute(query, params_values)
        except Exception as e:
            log.exception(f'\r\nException: {e}')
        finally:
            log.warning(textwrap.fill(f'UPDATE "{table_name}" SET {update_dict} WHERE {where_condition}', 115,
                                      subsequent_indent='                       '))


class DataBase(DataBaseMain):
    def __init__(self, dsn: str):
        super().__init__(dsn)

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
                    f'Value "{specific_field_name}" from {table_name} received successfully : {data_with_pk[0][idx]}')
                return {specific_field_name: data_with_pk[0][idx]}

    # - FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN ---F
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
    def __init__(self):
        self.name = None
        self.password = None
        self.create_dsn_string()
        self.cur = self.connection()

        self.create_table_beam_tasks()
        self.create_table_primary_marks()
        self.create_table_candidates_history()
        self.create_table_candidates()
        self.create_table_air_tracks_history()
        self.create_table_air_tracks()
        self.create_table_forb_sectors()

    def create_dsn_string(self):
        print(f'Enter name of DataBase')
        self.name = input()
        print(f'Enter password of DataBase')
        self.password = input()

    def connection(self):
        con = psycopg2.connect(dbname=self.name,
                               user='postgres', host='localhost',
                               password=self.password)
        con.autocommit = True
        cur = con.cursor()
        log.info(f'DataBase connection complete')
        return cur

    def create_table_beam_tasks(self):
        query = """CREATE TABLE public."BeamTasks"
        (
        "BeamTask" serial PRIMARY KEY,
        "taskId" integer,
        "isFake" boolean,
        "trackId" integer,
        "taskType" integer,
        "viewDirectionId" integer,
        "antennaId" integer,
        "pulsePeriod" real,
        threshold real,
        "lowerVelocityTrim" real,
        "upperVelocityTrim" real,
        "lowerDistanceTrim" real,
        "upperDistanceTrim" real,
        "beamAzimuth" real,
        "beamElevation" real
        )"""
        self.cur.execute(query)

    def create_table_primary_marks(self):
        query = """CREATE TABLE public."PrimaryMarks"
        (
        "PrimaryMark" serial,
        "BeamTask" serial,
        "primaryMarkId" serial,
        "scanTime" real,
        "antennaId" integer,
        "beamAzimuth" real,
        "beamElevation" real,
        "azimuth" real,
        "elevation" real,
        "markType" integer,
        "distance" real,
        "dopplerSpeed" real,
        "signalLevel" real,
        "reflectedEnergy" real,
        CONSTRAINT "PrimaryMarks_pkey" PRIMARY KEY ("PrimaryMark"),
        CONSTRAINT "PrimaryMarks_BeamTask_fkey" FOREIGN KEY ("BeamTask")
        )"""
        self.cur.execute(query)

    def create_table_candidates_history(self):
        query = """CREATE TABLE public."CandidatesHistory"
        (
        "CandidatesHistory" serial PRIMARY KEY,
        "BeamTask" serial,
        "PrimaryMark" serial,
        "Candidate" serial,
        azimuth real,
        elevation real,
        state integer,
        "distanceZoneWeight" real,
        "velocityZoneWeight" real,
        "numDistanceZone" real,
        "numVelocityZone" real,
        "antennaId" integer,
        "nextTimeUpdate" real,
        CONSTRAINT "CandidatesHistory_pkey" PRIMARY KEY ("CandidatesHistory"),
        CONSTRAINT "Candidates_BeamTask_fkey" FOREIGN KEY ("BeamTask")
        CONSTRAINT "Candidates_CandidatesIds_fkey" FOREIGN KEY ("Candidate")
        CONSTRAINT "Candidates_PrimaryMark_fkey" FOREIGN KEY ("PrimaryMark")
        )"""
        self.cur.execute(query)

    def create_table_candidates(self):
        query = """CREATE TABLE public."Candidates"
        (
        "Candidate" serial PRIMARY KEY,
        id integer
        )"""
        self.cur.execute(query)

    def create_table_air_tracks_history(self):
        query = """CREATE TABLE public."AirTracksHistory"
        (
        "AirTracksHistory" serial PRIMARY KEY,
        "PrimaryMark" serial,
        "CandidatesHistory" serial,
        "AirTrack" serial,
        type integer,
        priority integer,
        "antennaId" integer,
        azimuth real,
        elevation real,
        distance real,
        "radialVelocity" real,
        "pulsePeriod" real,
        "missesCount" real,
        "possiblePeriods" real[],
        "nextTimeUpdate" integer,
        "scanPeriod" real,
        "sigmaAzimuth" real,
        "sigmaElevation" real,
        "sigmaDistance" real,
        "sigmaRadialVelocity" real,
        "minDistance" real,
        "maxDistance" real,
        "minRadialVelocity" real,
        "maxRadialVelocity" real,
        CONSTRAINT "AirTracks_pkey" PRIMARY KEY ("AirTracksHistory"),
        CONSTRAINT "AirTracksHistory_AirTrack_fkey" FOREIGN KEY ("AirTrack")
        CONSTRAINT "AirTracks_Candidate_fkey" FOREIGN KEY ("CandidatesHistory")
        CONSTRAINT "AirTracks_PrimaryMark_fkey" FOREIGN KEY ("PrimaryMark")
        )"""
        self.cur.execute(query)

    def create_table_air_tracks(self):
        query = """CREATE TABLE public."AirTracks"
        (
        "AirTrack" serial PRIMARY KEY),
        id integer)
        )"""
        self.cur.execute(query)

    def create_table_forb_sectors(self):
        query = """CREATE TABLE public."ForbiddenSectors"
        (
        "ForbiddenSector" serial PRIMARY KEY,
        "azimuthBeginNSSK" real,
        "azimuthEndNSSK" real,
        "elevationBeginNSSK" real,
        "elevationEndNSSK" real,
        "nextTimeUpdate" integer,
        "isActive" boolean)
        )"""
        self.cur.execute(query)
