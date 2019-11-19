# ALTER SEQUENCE "Candidates_Candidate_seq" restart with 1;


# ALTER
# SEQUENCE
# "PrimaryMarks_PrimaryMark_seq"
# restart
# with 1;


# ALTER
# SEQUENCE
# "Candidates_Candidate_seq"
# restart
# with 1;


# SELECT DISTINCT "taskId", "taskType", "antennaId"
# FROM public."BeamTasks"
# ORDER BY "taskId"
# ;


# SELECT "BeamTask", "taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
# threshold, "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim", "upperDistanceTrim", "betaBSK",
# "epsilonBSK"
# FROM public."BeamTasks"
# where "trackId" != 0
# ;


# SELECT "BeamTask", "taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId",
# "pulsePeriod", threshold, "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
# "upperDistanceTrim", "betaBSK", "epsilonBSK"
# FROM public."BeamTasks"
# where "taskType" != 0
# and "taskType" != 1
# ;


# def insert_to(self, table_name: str, dict_to_insert: dict):
#     # формирование строки запроса
#     columns = ','.join([f'"{x[0]}"' for x in data])
#     param_values = tuple(x[1] for x in data)


# class TelemetryReader:
#     def __init__(self, file_name_str: str, data_struct: list, frame_size: int, frame_rate_file: str):
#         self.file_name_str = file_name_str
#         self.data_struct = data_struct
#         self.frame_size = frame_size
#         self.frame_rate_file = frame_rate_file
#
#         self.start_frame = self.read_start_frame()
#         self.frames_count = self.frame_counter()
#
#     def write_start_frame(self, frame_number):
#         if self.frame_rate_file.is_file():
#             prev_frame_number = {'prev_frame_number': frame_number - 1}
#             with open(self.frame_rate_file, 'w') as fr_c:
#                 fr_c.write(json.dumps(prev_frame_number))
#             return prev_frame_number['prev_frame_number']
#         else:
#             prev_frame_number = {'prev_frame_number': frame_number - 1}
#             with open(self.frame_rate_file, 'w+') as fr_c:
#                 fr_c.write(json.dumps(prev_frame_number))
#             return prev_frame_number['prev_frame_number']
#
#     def read_start_frame(self):
#         if self.frame_rate_file.is_file():
#             prev_frame_number = {'prev_frame_number': 0}
#             with open(self.frame_rate_file) as fr_c:
#                 prev_frame_number.update(json.load(fr_c))
#             return prev_frame_number['prev_frame_number']
#
#         else:
#             prev_frame_number = {'prev_frame_number': 0}
#             with open(self.frame_rate_file, 'w+') as fr_c:
#                 fr_c.write(json.dumps(prev_frame_number))
#             return prev_frame_number['prev_frame_number']
#
#
# def change_name_of_binary_data(func):
#     def wrapper(*args, **kwargs):
#         result = func(*args, **kwargs)
#         for i in result:
#             i['beamAzimuth'] = i.pop('betaBSK')
#             i['beamElevation'] = i.pop('epsilonBSK')
#             if 'isFake' in i:
#                 v = bool(i.get('isFake'))
#                 i.update({'isFake': v})
#         return result
#
#     return wrapper


# @staticmethod
# def map_values(data: dict) -> dict:
#     z = []
#     returned_data = {}
#     for k, v in data.items():
#         if 'isFake' in k:
#             data['isFake'] = bool(v)
#             if data['isFake']:
#                 raise Exception
#         elif 'processingTime' in k:
#             returned_data['scanTime'] = data['processingTime']
#         elif 'distancePeriod' in k:
#             returned_data['distanceZoneWeight'] = data['distancePeriod']
#         elif 'velocityPeriod' in k:
#             returned_data['velocityZoneWeight'] = data['velocityPeriod']
#         elif 'betaBSK' in k:
#             returned_data['beamAzimuth'] = data['betaBSK']
#         elif 'epsilonBSK' in k:
#             returned_data['beamElevation'] = data['epsilonBSK']
#         elif 'type' in k:
#             returned_data['markType'] = data['type']
#         elif re.search(r'\bdistance\b', k):
#             returned_data['numDistanceZone'] = data['resolvedDistance']
#         elif re.search(r'\bvelocity\b', k):
#             returned_data['numVelocityZone'] = data['resolvedVelocity']
#         elif 'possiblePeriod[' in k:
#             z.append(v)
#         elif 'scanPeriodSeconds' in k:
#             returned_data['scanPeriod'] = data['scanPeriodSeconds']
#         elif 'nextUpdateTimeSeconds' in k:
#             returned_data['nextTimeUpdate'] = data['nextUpdateTimeSeconds']
#         elif 'creationTimeSeconds' in k:
#             returned_data['nextTimeUpdate'] = data['creationTimeSeconds']
#
#     if len(z) == 6:
#         returned_data.update({'possiblePeriods': z})


#     def data_base_restore(self):
#         dsn = self.dsn.split()[1:]
#         conn = psycopg2.connect(dsn)
#         conn.autocommit = True
#         cur = conn.cursor()
#         queryies = ("""
#                       CREATE TABLE public."BeamTasks"
# (
#         "BeamTask" serial PRIMARY KEY,
#         "taskId" integer,
#         "isFake" boolean,
#         "trackId" integer,
#         "taskType" integer,
#         "viewDirectionId" integer,
#         "antennaId" integer,
#         "pulsePeriod" real,
#         threshold real,
#         "lowerVelocityTrim" real,
#         "upperVelocityTrim" real,
#         "lowerDistanceTrim" real,
#         "upperDistanceTrim" real,
#         "beamAzimuth" real,
#         "beamElevation" real
# )
#         """,
#                     CREATE TABLE public."PrimaryMarks"
# (
#     "PrimaryMark" serial,
#     "BeamTask" serial,
#     "primaryMarkId" serial,
#     "scanTime" real,
# 	  "antennaId" integer,
# 	  "beamAzimuth" real,
#     "beamElevation" real,
#     "azimuth" real,
#     "elevation" real,
#     "markType" integer,
#     "distance" real,
#     "dopplerSpeed" real,
#     "signalLevel" real,
#     "reflectedEnergy" real,
#     CONSTRAINT "PrimaryMarks_pkey" PRIMARY KEY ("PrimaryMark"),
#     CONSTRAINT "PrimaryMarks_BeamTask_fkey" FOREIGN KEY ("BeamTask")
# )
#         """,
#                     """CREATE TABLE public."CandidatesHistory"
# (
#     "CandidatesHistory" serial PRIMARY KEY,
#     "BeamTask" serial,
#     "PrimaryMark" serial,
#     "Candidate" serial,
#     azimuth real,
#     elevation real,
#     state integer,
#     "distanceZoneWeight" real,
#     "velocityZoneWeight" real,
#     "numDistanceZone" real,
#     "numVelocityZone" real,
#     "antennaId" integer,
#     "nextTimeUpdate" real,
#     CONSTRAINT "CandidatesHistory_pkey" PRIMARY KEY ("CandidatesHistory"),
#     CONSTRAINT "Candidates_BeamTask_fkey" FOREIGN KEY ("BeamTask")
#     CONSTRAINT "Candidates_CandidatesIds_fkey" FOREIGN KEY ("Candidate")
#     CONSTRAINT "Candidates_PrimaryMark_fkey" FOREIGN KEY ("PrimaryMark")
# )
#
#         """,
#                     """CREATE TABLE public."Candidates"
# (
#     "Candidate" serial PRIMARY KEY,
#     id integer)
#
#
#         """,
#                     """CREATE TABLE public."AirTracksHistory"
# (
#     "AirTracksHistory" serial PRIMARY KEY,
#     "PrimaryMark" serial,
#     "CandidatesHistory" serial,
#     "AirTrack" serial,
#     type integer,
#     priority integer,
#     "antennaId" integer,
#     azimuth real,
#     elevation real,
#     distance real,
#     "radialVelocity" real,
#     "pulsePeriod" real,
#     "missesCount" real,
#     "possiblePeriods" real[],
#     "nextTimeUpdate" integer,
#     "scanPeriod" real,
#     "sigmaAzimuth" real,
#     "sigmaElevation" real,
#     "sigmaDistance" real,
#     "sigmaRadialVelocity" real,
#     "minDistance" real,
#     "maxDistance" real,
#     "minRadialVelocity" real,
#     "maxRadialVelocity" real,
#     CONSTRAINT "AirTracks_pkey" PRIMARY KEY ("AirTracksHistory"),
#     CONSTRAINT "AirTracksHistory_AirTrack_fkey" FOREIGN KEY ("AirTrack")
#     CONSTRAINT "AirTracks_Candidate_fkey" FOREIGN KEY ("CandidatesHistory")
#     CONSTRAINT "AirTracks_PrimaryMark_fkey" FOREIGN KEY ("PrimaryMark")
#
#         """,
#                     """CREATE TABLE public."AirTracks"
# (
#     "AirTrack" serial PRIMARY KEY),
#     id integer)
#
#         """,
#                     """CREATE TABLE public."ForbiddenSectors"
# (
#     "ForbiddenSector" serial PRIMARY KEY,
#     "azimuthBeginNSSK" real,
#     "azimuthEndNSSK" real,
#     "elevationBeginNSSK" real,
#     "elevationEndNSSK" real,
#     "nextTimeUpdate" integer,
#     "isActive" boolean)
#         """)
#         for query in queryies:
#             cur.execute(query)
#         print('s')
# def nullify_the_sequences(self, table_name: str, seq_name: str):
#     query = f'ALTER SEQUENCE "{table_name}_{seq_name}_seq" restart with 1'
#     try:
#         self.cur.execute(query)
#     except Exception as e:
#         log.exception(f'\r\nException: {e}')
#     finally:
#         log.warning(f'ALTER SEQUENCE "{table_name}_{seq_name}_seq" restart with 1')
