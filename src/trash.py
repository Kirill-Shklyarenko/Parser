# class Data_structure:
#         def __init__(self):
#             self.file = self.open()
#             self.frame_size = self.find_frame_size()
#             self.frames_count = self.find_count_of_frames()
#             self.data_structure = self.do_structure()
#
#         @staticmethod
#         def open():
#             with open(planner) as file:
#                 data = file.readlines()
#                 return data
#
#         def find_count_of_frames(self):
#             file_size = os.path.getsize(planner_RSF)  # Размер файла в байтах
#             file_size = file_size - 14  # отсекаем 14 байт заголовка
#             try:
#                 frames_count = file_size / (self.frame_size * 2)
#             except ZeroDivisionError as e:
#                 print(frames_count)
#                 print(e)
#             else:
#                 return int(frames_count)
#
#         def do_structure(self):
#             group = []
#             substring = []  # список содержит имя "NavigationData"[0] и словарь "Parameters"[1]
#
#             for i, line in enumerate(self.file):
#                 line = line.split()
#
#                 # Поиск имени группы
#                 if ';' in line[0]:
#                     next_line = self.file[i + 1].split()
#                     if ';' not in next_line[0]:
#                         if substring:
#                             group.append(copy.copy(substring))
#                             substring.clear()
#                         line.remove(';')
#                         nwline = ''.join(line)
#                         substring.append(nwline)
#                     else:
#                         group.append(copy.copy(substring))
#                         substring.clear()
#
#                 # Поиск описания переменных
#                 elif len(line) > 3:
#                     if 'UU' in line[5]:
#                         params = {
#                             'name': line[0],
#                             'type': line[5],
#                             'offset': int(line[1]) - 1
#                         }
#                         substring.append(params)
#                     elif 'LL' in line[5]:
#                         params = {
#                             'name': line[0],
#                             'type': line[5],
#                             'offset': int(line[1]) - 1
#                         }
#                         substring.append(params)
#                     else:
#                         params = {
#                             'name': line[0],
#                             'type': line[5],
#                             'offset': int(line[1])
#                         }
#                         substring.append(params)
#             return group
#
#         def find_frame_size(self):
#             # Поиск размера блока данных
#             for i, line in enumerate(self.file):
#                 if i >= 1:
#                     break
#                 line = line.split()
#                 return int(line[0])
#
#
#     class Parsed_data(Data_structure):
#         def __init__(self, frame_number):
#             Data_structure.__init__(self)
#             self.frame_number = frame_number
#             self.data = self.parse_bin_file()
#
#         def parse_bin_file(self):
#             data_with_values = copy.deepcopy(self.data_structure)
#             frame_rate = self.frame_number * self.frame_size
#             for index, line in enumerate(data_with_values):
#                 for i in line:
#                     if type(i) == dict:
#                         type_w = i.get('type')
#                         offset = i.get('offset')
#                         value = byte_reader(type_w, offset)
#                         i.pop('type')
#                         i.pop('offset')
#                         i.update({'value': value})
#             return data_with_values
#
#         def find(self, name_to_find):
#             finded_data = []
#             for group in self.data:
#                 name = group[0]
#                 if re.search(name_to_find, name):
#                     finded_data.append(group)
#             return finded_data
#
#         def insert_to_bd(self):
#             pass
#
#
#     data_structure = Data_structure()
#     for frame_number in range(data_structure.frames_count):
#         data = Parsed_data(frame_number)
#         beam_tasks = data.find('beamTask')
#         beam_tasks.insert_to_bd
#         group_with_values = Parsed_data(frame_number)
#         beam_tasks = group_with_values.find('beamTask')
#         print('s')


# Находим группы по "ключевому слову"
# bt, id = find_group(data, 'beamTask')
# item = ['Task', 'taskId']  # [Groupname, parameter] what need to find
# bt_item = find_item(data, item)
# # Добавляем значения из других групп
# add_to(bt, bt_item)
# # Подготавливаем данные для вставки в таблицу
# bt_transformed = read_data('BeamTasks', bt, cur)
# # Вставляем группы в бд
# insert_into('BeamTasks', bt_transformed, cur)
# print(105 * '*')
# # ---------------------ЗАПОЛНЯЕМ "PrimaryMarks"----------------------#
# entity_c = entity_counter(data, 'primaryMark')
# id = 0
# for entity in range(entity_c):
#     if entity == 3:
#         breakpoint()
#     pm, id = find_group(data, 'primaryMark', id)
#     item = ['scanData', 'processingTime',
#             'scanData', 'taskId',
#             'scanData', 'antennaId']
#     pm_item = find_item(data, item, id)
#
#     bt_task_id = False
#     bt_antenna_id = [1, 2, 3, 4]
#     pm_task_id = False
#     pm_antenna_id = False
#
#     for group in bt:
#         for i in group:
#             if type(i) is dict:
#                 if 'taskId' in i:
#                     bt_task_id = i.get('taskId')
#                     break
#
#     for i in pm_item:
#         if 'taskId' in i: pm_task_id = i.get('taskId')
#         if 'antennaId' in i: pm_antenna_id = i.get('antennaId')
#         if pm_task_id and pm_antenna_id: break
#
#     if pm_task_id == bt_task_id and pm_antenna_id == bt_antenna_id:
#         # Some convertings with pm
#         add_to(pm, pm_item)
#
#         # insert_into_bd(pm, cur, 'PrimaryMarks')
#         print(105 * '*')








# data_find_methods.py
# import re
# import copy
#
#
# def create_group(data: list) -> list:
#     group = []  # список элементов [000, 001, 002]
#     substring = []  # который соержит имя "NavigationData, Flags, Beamtask" etc
#     params = {}  # со словарем из параметров "Lon, Lat" etc
#     cnt = 0
#     for line in data:
#         if type(line) is str:
#             cnt += 1
#             if cnt > 1:
#                 substring.append(copy.copy(params))
#                 params.clear()
#                 group.append(copy.copy(substring))
#                 substring.clear()
#             substring.append(line)
#         elif type(line) is list:
#             params[line[0]] = line[1]
#     return group
#
#
# def entity_counter(data: list, keyword: str) -> int:
#     first_string_in_match = False
#     gap = False
#     matches_count = 0
#     entity_c = 0
#     for group in data:
#         name = group[0]
#
#         if re.search(keyword, name) and matches_count == 0:
#             first_string_in_match = True
#             matches_count += 1
#         elif re.search(keyword, name) and first_string_in_match and not gap:
#             matches_count += 1
#         elif re.search(keyword, name) and gap:
#             gap = False
#             matches_count = 0
#             entity_c += 1
#         elif matches_count >= 1:
#             gap = True
#     return entity_c + 1
#
#
# def find_group(data: list, keyword: str, id=0) -> tuple:
#     finded_data = []
#     first_string_in_match = False
#     gap = False
#     matches_count = 0
#     prev_id = id
#     for id, group in enumerate(data):
#         name = group[0]
#         if id > prev_id:
#
#             if re.search(keyword, name) and matches_count == 0:
#                 first_string_in_match = True
#                 matches_count += 1
#                 finded_data.append(group)
#             elif re.search(keyword, name) and first_string_in_match and not gap:
#                 matches_count += 1
#                 finded_data.append(group)
#             elif re.search(keyword, name) and gap:
#                 return finded_data, id - 2
#             elif matches_count >= 1:
#                 gap = True
#     return finded_data, id - 2
#
#
# def find_item(data: list, item: list, id=0) -> list:
#     finded_data = []
#     names = []
#     params = []
#     if id:
#         data = data[:id]
#         data = list(reversed(data))
#     for i, k in enumerate(item):
#         index = i + 1
#         if index % 2 == 0:
#             params.append(k)
#         else:
#             names.append(k)
#
#     for group in data:
#         for name in names:
#             if name in group[0]:
#                 for i in group:
#                     if type(i) is dict:
#                         key = [x for x in i][0]
#                         for param in params:
#                             if key == param:
#                                 finded_data.append(i)
#                                 if len(finded_data) == len(params):
#                                     return finded_data
#                             else:
#                                 continue
#
#
# def add_to(group: list, item: list):
#     for i in group:
#         for val in item:
#             i.append(val)
