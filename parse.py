from struct import *
import os
import copy

planner = r'Planner'
planner_RSF = r'Planner.rsf'


def nxt_line(number_of_line):
    with open(planner) as file:
        line = file.readlines()[number_of_line - 1: number_of_line]
        line = line[0].split()
        return line


def byte_reader(type_w, offset):
    with open(planner_RSF, 'rb') as file:
        header = file.read(14).decode('cp1252')  # Имя файла заголовка [0 - 14]
        offset *= 2  # Номер слова в блоке умножаем на размер слова (2 байта)
        file.seek(offset + 14)  # Прибавляем 14 байт, чтобы отсечь Имя файла заголовка

        if 'WW' in type_w:
            type_w = 'I'  # UINT_2t
            size = 2

        elif 'SS' in type_w:
            type_w = 'i'  # INT_2t
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


def parse_planner_stn():
    number_of_line = 1
    struct = []
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
                    struct.append(next_line)
                    number_of_line += 1
                else:
                    struct.append(nwline)
                    number_of_line += 1
            # Поиск описания переменных
            elif len(line) > 3:
                if 'UU' in line[5]:
                    ca = [line[0], line[5], int(line[1])]
                    struct.append(ca)
                    number_of_line += 2
                elif 'LL' in line[5]:
                    ca = [line[0], line[5], int(line[1])]
                    struct.append(ca)
                    number_of_line += 2
                else:
                    ca = [line[0], line[5], int(line[1])]
                    struct.append(ca)
                    number_of_line += 1

    return struct, frame_size


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


def parse_planner_rsf(struct, frame_size, frame):
    struct_with_values = copy.deepcopy(struct)
    frame_rate = frame * frame_size
    for string in struct_with_values:
        if len(string) == 3:
            name = string[0]
            type_w = string[1]
            offset = string[2] + frame_rate

            value = byte_reader(type_w, offset)
            string.clear()
            string.insert(0, name)
            string.insert(1, value)


    return struct_with_values


if __name__ == "__main__":
    # 1) Парсим текстовый файл
    struct = parse_planner_stn()
    # 2) Вычисляем количество кадров
    frame_c = frame_counter(struct[1])
    # 3) Парсим бинарник по кадрам
    for frame in range(frame_c):
        print('FRAME № %s\r\n' % frame)

        struct_with_values = parse_planner_rsf(struct[0], frame_c, frame)

        for s in struct_with_values: print(s)

        for i in range(50):
            print(250 * '*')
        if frame == 1:
           hh=78
