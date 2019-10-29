from struct import *
import os
import copy
import re
import psycopg2

planner = r'Planner'
planner_RSF = r'Planner.rsf'


def byte_reader(type_w, offset):
    with open(planner_RSF, 'rb') as file:
        offset *= 2  # Номер слова в блоке умножаем на размер слова (2 байта)
        file.seek(offset + 14)  # Прибавляем 14 байт, чтобы отсечь Имя файла заголовка

        if 'WW' in type_w:
            type_w = 'I'  # UINT_2
            size = 2
        elif 'SS' in type_w:
            type_w = 'i'  # INT_2
            size = 2
        elif 'UU' in type_w:
            type_w = '<i'
            size = 4  # Размер 4 байта потому что используется 2 слова х 2 байта идущие друг за другом
        elif 'LL' in type_w:
            type_w = '<i'
            size = 4  # Размер 4 байта потому что используется 2 слова х 2 байта идущие друг за другом
        elif 'RR' in type_w:
            type_w = 'c'  # битовая переменная
            size = 1  # Размер 1 байт
        elif 'FF' in type_w:
            type_w = 'f'
            size = 4  # 2 слова х 2 байта(размер слова)

        word = file.read(size)
        value = unpack(type_w, word)[0]
    return value


def nxt_line(number_of_line):
    with open(planner) as file:
        line = file.readlines()[number_of_line - 1: number_of_line]
        line = line[0].split()
    return line


def parse_text_file():
    number_of_line = 1
    group = []  # просто список элементов [0, 1, 2]
    substring = []  # список содержит имя "NavigationData"[0] и словарь "Parameters"[1]

    with open(planner) as file:
        for line in file:
            line = line.split()
            # Поиск размера блока данных
            if len(line) == 1 and ';' not in line[0]:
                next_line = nxt_line(number_of_line + 1)
                if len(next_line) == 1 and ';' not in next_line[0]:
                    frame_size = int(line[0])
                    number_of_line += 2

            # Поиск имени группы
            elif ';' in line[0]:
                next_line = nxt_line(number_of_line + 1)
                if ';' not in next_line[0]:
                    if substring:
                        group.append(copy.copy(substring))
                        substring.clear()
                    line.remove(';')
                    nwline = ''.join(line)
                    substring.append(nwline)
                    number_of_line += 1
                else:
                    group.append(copy.copy(substring))
                    substring.clear()
                    number_of_line += 1

            # Поиск описания переменных
            elif len(line) > 3:
                if 'UU' in line[5]:
                    params = {
                        'name': line[0],
                        'type': line[5],
                        'offset': int(line[1]) - 1
                    }
                    substring.append(params)
                    number_of_line += 2
                elif 'LL' in line[5]:
                    params = {
                        'name': line[0],
                        'type': line[5],
                        'offset': int(line[1]) - 1
                    }
                    substring.append(params)
                    number_of_line += 2
                else:
                    params = {
                        'name': line[0],
                        'type': line[5],
                        'offset': int(line[1])
                    }
                    substring.append(params)
                    number_of_line += 1
    return group, frame_size


def parse_bin_file(data, frame_size, frame_number):
    data_with_values = copy.deepcopy(data)
    frame_rate = frame_number * frame_size
    for index, line in enumerate(data_with_values):
        for i in line:
            if type(i) == dict:
                name = i.get('name')
                type_w = i.get('type')
                offset = i.get('offset')
                value = byte_reader(type_w, offset + frame_rate)
                i.clear()
                i.update({name : value})
    return data_with_values


def create_group(data):
    group = []  # просто список элементов [000, 001, 002]
    substring = []  # который соержит имя "NavigationData, Flags, Beamtask" etc
    params = {}  # со словарем из параметров "Lon, Lat" etc
    cnt = 0
    for line in data:
        if type(line) is str:
            cnt += 1
            if cnt > 1:
                substring.append(copy.copy(params))
                params.clear()
                group.append(copy.copy(substring))
                substring.clear()
            substring.append(line)
        elif type(line) is list:
            params[line[0]] = line[1]
    return group


def frame_counter(frame_size):
    file_size = os.path.getsize(planner_RSF)  # Размер файла в байтах
    file_size = file_size - 14  # отсекаем 14 байт заголовка
    try:
        frames_count = file_size / (frame_size * 2)
    except ZeroDivisionError as e:
        print(frames_count)
        print(e)
    else:
        frames_count = int(frames_count)
    return frames_count


def find_group(group, name_to_find):
    finded_data = []
    for node in group:
        name = node[0]
        if re.search(name_to_find, name):
            finded_data.append(node)
    return finded_data


def connection():
    conn = psycopg2.connect(dbname='telemetry', user='postgres',
                            password='123', host='localhost')
    conn.autocommit = True
    cur = conn.cursor()
    return cur, conn


def execute(data_to_insert, table_name, cur):
    # Преобразование типов (int ---> bool)
    for string in data_to_insert:
        if 'isFake' in string[0]:
            string[1] = bool(string[1])
        if 'hasMatchedTrack' in string[0]:
            string[1] = bool(string[1])

    # формирование строки запроса
    columns = ','.join([f'"{x[0]}"' for x in data_to_insert])
    param_placeholders = ','.join(['%s' for x in range(len(data_to_insert))])
    query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
    param_values = tuple(x[1] for x in data_to_insert)
    try:
        cur.execute(query, param_values)
    except Exception as e:
        print(f'\r\nException: {e}')
    else:
        print(query, param_values)


def insert_into_bd(data, cur, table_name):
    data_to_insert = []

    # Для того чтобы узнать имена полей таблицы
    cur.execute(f'SELECT * FROM "{table_name}";')
    col_names = []
    for elt in cur.description:
        col_names.append(elt[0])

    for node in data:
        for i in node:
            if type(i) is dict:
                k = list(i.keys())[0]
                if k in col_names:
                    items = [[k, v] for k, v in i.items()] [0]
                    data_to_insert.append(items)

        execute(data_to_insert, table_name, cur)
        data_to_insert.clear()


if __name__ == "__main__":
    # Парсим текстовый файл
    data_structure, frame_size = parse_text_file()
    # Вычисляем количество кадров
    frame_c = frame_counter(frame_size)
    # Соединяемся с БД
    cur, conn = connection()
    # Парсим свинарник по кадрам
    for frame_number in range(frame_c):
        print('\r\nFRAME № %s \r\n' % frame_number)
        data = parse_bin_file(data_structure, frame_size, frame_number)
        #---------------------ЗАПОЛНЯЕМ "BeamTasks"----------------------#
        # Находим группы по "ключевому слову"
        bt = find_group(data, 'beamTask')
        tasks = find_group(data, 'Task')
        task_id = [[k,v] for k, v in tasks[0][1].items()] [0]
        for group in bt:
            group.append(task_id)
        # Вставляем ее в бд
        insert_into_bd(bt, cur, 'BeamTasks')
        print(105 * '*')

        # ---------------------ЗАПОЛНЯЕМ "PrimaryMarks"----------------------#
        # Находим группы по "ключевому слову"
        pm = find_group(data, 'primaryMark')
        scan_data = find_group(data,'scanData')
        scan_time = {'name' : 'scanTime',
                     'value' : scan_data[0][1].get('value')}


        a = 1



    # class Data_structure:
    #     def __init__(self):
    #         self.file = self.open()
    #         self.frame_size = self.find_frame_size()
    #         self.frames_count = self.find_count_of_frames()
    #         self.data_structure = self.do_structure()
    #
    #     @staticmethod
    #     def open():
    #         with open(planner) as file:
    #             data = file.readlines()
    #             return data
    #
    #     def find_count_of_frames(self):
    #         file_size = os.path.getsize(planner_RSF)  # Размер файла в байтах
    #         file_size = file_size - 14  # отсекаем 14 байт заголовка
    #         try:
    #             frames_count = file_size / (self.frame_size * 2)
    #         except ZeroDivisionError as e:
    #             print(frames_count)
    #             print(e)
    #         else:
    #             return int(frames_count)
    #
    #     def do_structure(self):
    #         group = []
    #         substring = []  # список содержит имя "NavigationData"[0] и словарь "Parameters"[1]
    #
    #         for i, line in enumerate(self.file):
    #             line = line.split()
    #
    #             # Поиск имени группы
    #             if ';' in line[0]:
    #                 next_line = self.file[i + 1].split()
    #                 if ';' not in next_line[0]:
    #                     if substring:
    #                         group.append(copy.copy(substring))
    #                         substring.clear()
    #                     line.remove(';')
    #                     nwline = ''.join(line)
    #                     substring.append(nwline)
    #                 else:
    #                     group.append(copy.copy(substring))
    #                     substring.clear()
    #
    #             # Поиск описания переменных
    #             elif len(line) > 3:
    #                 if 'UU' in line[5]:
    #                     params = {
    #                         'name': line[0],
    #                         'type': line[5],
    #                         'offset': int(line[1]) - 1
    #                     }
    #                     substring.append(params)
    #                 elif 'LL' in line[5]:
    #                     params = {
    #                         'name': line[0],
    #                         'type': line[5],
    #                         'offset': int(line[1]) - 1
    #                     }
    #                     substring.append(params)
    #                 else:
    #                     params = {
    #                         'name': line[0],
    #                         'type': line[5],
    #                         'offset': int(line[1])
    #                     }
    #                     substring.append(params)
    #         return group
    #
    #     def find_frame_size(self):
    #         # Поиск размера блока данных
    #         for i, line in enumerate(self.file):
    #             if i >= 1:
    #                 break
    #             line = line.split()
    #             return int(line[0])
    #
    #
    # class Parsed_data(Data_structure):
    #     def __init__(self, frame_number):
    #         Data_structure.__init__(self)
    #         self.frame_number = frame_number
    #         self.data = self.parse_bin_file()
    #
    #     def parse_bin_file(self):
    #         data_with_values = copy.deepcopy(self.data_structure)
    #         frame_rate = self.frame_number * self.frame_size
    #         for index, line in enumerate(data_with_values):
    #             for i in line:
    #                 if type(i) == dict:
    #                     type_w = i.get('type')
    #                     offset = i.get('offset')
    #                     value = byte_reader(type_w, offset)
    #                     i.pop('type')
    #                     i.pop('offset')
    #                     i.update({'value': value})
    #         return data_with_values
    #
    #     def find(self, name_to_find):
    #         finded_data = []
    #         for group in self.data:
    #             name = group[0]
    #             if re.search(name_to_find, name):
    #                 finded_data.append(group)
    #         return finded_data
    #
    #     def insert_to_bd(self):
    #         pass
    #
    #
    # data_structure = Data_structure()
    # for frame_number in range(data_structure.frames_count):
    #     group_with_values = Parsed_data(frame_number)
    #     beam_tasks = group_with_values.find('beamTask')
    #     print('s')
