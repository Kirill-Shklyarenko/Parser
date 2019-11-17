# # ALTER SEQUENCE "Candidates_Candidate_seq" restart with 1;
#
#
# # ALTER
# # SEQUENCE
# # "PrimaryMarks_PrimaryMark_seq"
# # restart
# # with 1;
# #
# # ALTER
# # SEQUENCE
# # "Candidates_Candidate_seq"
# # restart
# # with 1;
#
#
#
# # SELECT DISTINCT "taskId", "taskType", "antennaId"
# # FROM public."BeamTasks"
# # ORDER BY "taskId"
# # ;
#
#
# # SELECT "BeamTask", "taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
# # threshold, "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim", "upperDistanceTrim", "betaBSK",
# # "epsilonBSK"
# # FROM public."BeamTasks"
# # where "trackId" != 0
# # ;
#
#
# # SELECT "BeamTask", "taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId",
# # "pulsePeriod", threshold, "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
# # "upperDistanceTrim", "betaBSK", "epsilonBSK"
# # FROM public."BeamTasks"
# # where "taskType" != 0
# # and "taskType" != 1
# # ;
#
#
# # def insert_to(self, table_name: str, dict_to_insert: dict):
# #     # формирование строки запроса
# #     columns = ','.join([f'"{x[0]}"' for x in data])
# #     param_values = tuple(x[1] for x in data)
#
#
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
#
#
# def adjust_to_col_names(func: funcfunction) -> function:
#     def wrapper(*args, **kwargs):
#         data = {}
#         res = []
#         result = func(*args, **kwargs)
#         columns_names = ["taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
#                          "threshold", "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
#                          "upperDistanceTrim", "beamAzimuth", "beamElevation"]
#         for i in result:
#             data.update({key: value for key, value in i.items() if key in columns_names})
#             res.append(data)
#         return res
#
#     return wrapper


# def __iter__(self):
#     return self.container[self.i]
#
# def __next__(self):
#
#     try:
#         result = self.container[self.i]
#     except IndexError:
#         raise StopIteration
#     self.i += 1
#     return result

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
#     data.pop('betaBSK')
#     data.pop('epsilonBSK')
#     returned_data.update(data)
#     return returned_data
