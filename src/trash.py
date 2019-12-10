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


"""
reg expr for Ideolog:
message pattern:         ^(\d{2}:\d{2}:\d{2})\s(.*)\s\d{2}\s\s\w*\s\s(.*)$
message start pattern:   ^\d
time format:             HH:mm:SS
groups:
                         1
                         3
                         2

"""
