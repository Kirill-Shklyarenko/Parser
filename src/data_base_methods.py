import logging.config
import textwrap

import psycopg2

log = logging.getLogger('simpleExample')


class DataBaseMain:
    __slots__ = ('dsn', 'cur')

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.cur = self.connection()

    def connection(self) -> any:
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
            log.warning(textwrap.fill(f'INSERT INTO "{table_name}" {data}', 100,
                                      subsequent_indent='                                      '))

    def read_from_table(self, table_name: str, dict_for_get_pk: dict) -> list:
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

    def get_pk_for_beam_tasks(self, full_block_dict: dict):
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

    def get_pk_for_primary_marks(self, full_block_dict: dict):
        table_name = 'PrimaryMarks'
        fields_for_get_pk = ['BeamTask']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_candidates(self, full_block_dict: dict):
        table_name = 'Candidates'
        fields_for_get_pk = ['id']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_air_tracks(self, full_block_dict: dict):
        table_name = 'AirTracks'
        fields_for_get_pk = ['id']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_cand_hists(self, full_block_dict: dict):
        table_name = 'CandidatesHistory'
        fields_for_get_pk = ['BeamTask', 'PrimaryMark']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_tracks_hists(self, full_block_dict: dict):
        table_name = 'AirTracksHistory'
        fields_for_get_pk = ['AirTracksHistory', 'PrimaryMark', 'CandidateHistory']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk

    def get_pk_for_forb_sectors(self, full_block_dict: dict):
        table_name = 'ForbiddenSectors'
        fields_for_get_pk = ['azimuthBeginNSSK', 'azimuthEndNSSK','elevationBeginNSSK','elevationEndNSSK']
        result = {}
        for k, v in full_block_dict.items():
            if k in fields_for_get_pk:
                result.update({k:v})
        pk = self.get_pk(table_name, result)
        return pk


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

    def connection(self) -> any:
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
