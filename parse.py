from struct import *
import os
import copy
import re

import psycopg2

planner = r'Planner'
planner_RSF = r'Planner.rsf'


def nxt_line(number_of_line):
    with open(planner) as file:
        line = file.readlines()[number_of_line - 1: number_of_line]
        line = line[0].split()
    return line


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


def parse_text_file():
    number_of_line = 1
    data = []
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
                line.remove(';')
                nwline = ''.join(line)
                # Проверка следующей строки (не является ли она именем группы)
                next_line = nxt_line(number_of_line + 1)
                if ';' in next_line[0]:
                    next_line.remove(';')
                    nwline = ''.join(next_line)
                data.append(nwline)
                number_of_line += 1

            # Поиск описания переменных
            elif len(line) > 3:
                if 'UU' in line[5]:
                    ca = [line[0], line[5], int(line[1]) - 1]
                    data.append(ca)
                    number_of_line += 2
                elif 'LL' in line[5]:
                    ca = [line[0], line[5], int(line[1]) - 1]
                    data.append(ca)
                    number_of_line += 2
                else:
                    ca = [line[0], line[5], int(line[1])]
                    data.append(ca)
                    number_of_line += 1
    return data, frame_size


def parse_bin_file(data, frame_size, frame_number):
    data_with_values = copy.deepcopy(data)
    frame_rate = frame_number * frame_size

    for line in data_with_values:
        if len(line) == 3:
            name = line[0]
            type_w = line[1]
            offset = line[2] + frame_rate

            value = byte_reader(type_w, offset)

            line.clear()
            line.insert(0, name)
            line.insert(1, value)
    return data_with_values


def frame_counter(frame_size):
    with open(planner_RSF, 'rb') as file:
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


# def find_in_structure(data, keyword):
#     finded_data = []
#     flag = False
#     for line in data:
#         if type(line) is str:
#             if re.search(keyword, line):
#                 flag = True
#             else:
#                 flag = False
#         if flag:
#             finded_data.append(line)
#     return finded_data


# def line_counter(data):
#     block_count = 0
#     line_count = 0
#     for string in data:
#         if type(string) is str:
#             block_count += 1
#         if type(string) is list and block_count == 1:
#             line_count += 1
#     return line_count


#def slicer(data, count_of_lines_in_data):
#    for string in data:
#        if type(string) is str:
#            data.remove(string)
#    for i in range(0, len(data), count_of_lines_in_data):
#        yield data[i:i + count_of_lines_in_data]


class Huyas():
    def __init__(self, data):
        self.data = data

        self.name = self.name()
        pass
        # self.
        # self.
        # self.
    def name(self):
        for s in data:
            if type(s) is str:
                pass


def create_group(data):
    group = []          # просто список элементов [000, 001, 002]
    substring = []      # который соержит имя "NavigationData, Flags, Beamtask" etc
    params = {}         # со словарем из параметров "Lon, Lat" etc
    cnt = 0
    for string in data:
        if type(string) is str:
            cnt += 1
            if cnt > 1:
                substring.append(copy.copy(params))
                params.clear()
                group.append(copy.copy(substring))
                substring.clear()
            substring.append(string)
        elif type(string) is list:
            params[string[0]] = string[1]
    return group


def find_group(group, name_to_find):
    print("Match Case? ----> Y/N")
    a = input()
    for node in group:
        name = node[0]
        if 'Y' in a:
            if name == name_to_find:
                print(node)
                return node
        else:
            if re.search(name_to_find, name):
                print(node)
                return node


def connection():
    conn = psycopg2.connect(dbname='telemetry', user='postgres',
                            password='123', host='localhost')
    conn.autocommit = True
    cur = conn.cursor()
    return cur, conn


def insert_beam_tasks(data, cur):
    table_name = 'BeamTasks'

    # Для того чтобы узнать имена полей таблицы
    cur.execute(f'SELECT * FROM "{table_name}";')
    col_names = []
    for elt in cur.description:
        col_names.append(elt[0])
    #print(f'Table "{table_name}" have columns: {col_names}')

    # чето другое
    data_to_insert = []
    
    for key, value in data[1].items():
        if key in col_names:
            substr_to_insert = []
            substr_to_insert.append(key)
            substr_to_insert.append(value)
            data_to_insert.append(substr_to_insert)

    # int(0) ----> to False
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


if __name__ == "__main__":
    # 1) Парсим текстовый файл
    struct = parse_text_file()
    data = struct[0]
    frame_size = struct[1]
    # 2) Вычисляем количество кадров
    frame_c = frame_counter(frame_size)
    # Соединяемся с БД
    cur, conn = connection()
    # 3) Парсим свинарник по кадрам
    for frame_number in range(frame_c):
        print('\r\nFRAME № %s \r\n' % frame_number)

        # Возможно придется обьеденить два метода:
        struct_with_values = parse_bin_file(data, frame_size, frame_number) #   ЭТОТ
        #group = create_group(struct_with_values)                            # И ЭТОТ
        d = Huyas(struct_with_values)


        # Находим ноду по "ключевому слову" в группах
        name_to_find = 'beamTask'
        i_bt = find_group(group, name_to_find)

        # Вставляем ее в бд
        insert_beam_tasks(i_bt, cur)



        # for s in fdata: print(s)
        for i in range(5): print(105 * '*')

        if frame_number == 1:
            breakpoint()
