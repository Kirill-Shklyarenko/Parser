from struct import *
import psycopg2



planner = r'Planner'
planner_RSF = r'Planner.rsf'


def line_parser(number_of_line):
    with open(planner) as file:
        line = file.readlines()[number_of_line - 1: number_of_line]
        line = line[0].split()
        return line

def value_of_lines():
    with open(planner) as file:
        lines = file.readlines()
        return int(len(lines))

def byte_reader(type_w, size, offset):
    with open(planner_RSF, 'rb') as file:
        header = file.read(14).decode('cp1252')  # Имя файла заголовка [0 - 14]
        offset *= 2  # Номер слова в блоке умножаем на размер слова (2 байта)
        file.seek(offset + 14)  # Прибавляем 14 байт, чтобы отсечь Имя файла заголовка
        word = file.read(size)
        value = unpack(type_w, word)[0]
        # print('BYTES: ' + str(word))
        # print('VALUE: ' + str(value))
        return value

def parse_planner_stn(frame_start, frame_end):
    number_of_line = frame_start

    vol = frame_end
    struct = []
    while number_of_line < vol:
        line = line_parser(number_of_line)
        # Поиск размера блока данных
        # if len(line) == 1 and ';' not in line[0]:
        #     next_line = line_parser(number_of_line + 1)
        #     if len(next_line) == 1 and ';' not in next_line[0]:
        #         number_of_line += 2
        # Поиск имени группы
        if ';' in line[0]:
            line.remove(';')
            nwline = ''.join(line)
            # Проверка следующей строки (не является ли она именем группы)
            next_line = line_parser(number_of_line + 1)
            if ';' in next_line[0]:
                struct.append(next_line)
                number_of_line += 1
            else:
                struct.append(nwline)
                number_of_line += 1
        # Поиск описания переменных
        elif len(line) > 3:
            # Определяем тип переменной
            if 'WW' in line[5]:
                ca = [line[0], line[5], int(line[1])]
                struct.append(ca)
                number_of_line += 1
            elif 'SS' in line[5]:
                ca = [line[0], line[5], int(line[1])]
                struct.append(ca)
                number_of_line += 1
            elif 'UU' in line[5]:
                next_line = line_parser(number_of_line + 1)
                prev_offset = int(line[1])
                curr_offset = int(next_line[0])
                ca = [line[0], line[5], [curr_offset, prev_offset]]
                struct.append(ca)
                number_of_line += 2
            elif 'LL' in line[5]:
                next_line = line_parser(number_of_line + 1)
                prev_offset = int(line[1])
                curr_offset = int(next_line[0])
                ca = [line[0], line[5], [curr_offset, prev_offset]]
                struct.append(ca)
                number_of_line += 2
            elif 'RR' in line[5]:
                ca = [line[0], line[5], int(line[1])]
                struct.append(ca)
                number_of_line += 1
            elif 'FF' in line[5]:
                ca = [line[0], line[5], int(line[1])]
                struct.append(ca)
                number_of_line += 1
    return struct

def parse_planner_rsf(struct):
    for string in struct:
        if len(string) == 3:
            if 'WW' in string[1]:
                type_w = 'I'  # UINT_2t
                size = 2
                offset = string[2]
                name = string[0]
                value = byte_reader(type_w, size, offset)
                string.clear()
                string.insert(0, name)
                string.insert(1, value)
            elif 'SS' in string[1]:
                type_w = 'i'  # INT_2t
                size = 2
                offset = string[2]
                name = string[0]
                value = byte_reader(type_w, size, offset)
                string.clear()
                string.insert(0, name)
                string.insert(1, value)
            elif 'UU' in string[1]:
                type_w = '<i'
                size = 4  # Размер 4 байта потому что используется 2 слова х 2 байта идущие друг за другом
                offset = string[2][0]
                name = string[0]
                value = byte_reader(type_w, size, offset)
                string.clear()
                string.insert(0, name)
                string.insert(1, value)
            elif 'LL' in string[1]:
                type_w = '<i'
                size = 4  # Размер 4 байта потому что используется 2 слова х 2 байта идущие друг за другом
                offset = string[2][0]
                name = string[0]
                value = byte_reader(type_w, size, offset)
                string.clear()
                string.insert(0, name)
                string.insert(1, value)
            elif 'RR' in string[1]:
                type_w = 'c'  # битовая переменная
                size = 1      # Размер 1 байт
                offset = string[2]
                name = string[0]
                value = byte_reader(type_w, size, offset)
                string.clear()
                string.insert(0, name)
                string.insert(1, value)
            elif 'FF' in string[1]:
                type_w = 'f'
                size = 4  # 2 слова х 2 байта(размер слова)
                offset = string[2]
                name = string[0]
                value = byte_reader(type_w, size, offset)
                string.clear()
                string.insert(0, name)
                string.insert(1, value)
    return struct


def parse_by_frames():
    number_of_line = 1
    frame_count = 0
    vol = value_of_lines()
    while number_of_line < vol:
        line = line_parser(number_of_line)
        # Поиск размера блока данных
        if len(line) == 1 and ';' not in line[0]:
            next_line = line_parser(number_of_line + 1)
            if len(next_line) == 1 and ';' not in next_line[0]:
                number_of_line += 2
                # frame_size = int(line[0])
                frame_count += 1
                frame_start = number_of_line
        else:
            frame_end = number_of_line
            number_of_line += 1
    return frame_count, frame_start, frame_end


if __name__ == "__main__":
    # 1) Парсим текстовый файл planner.stn
    #struct = parse_planner_stn()
    #for s in struct: print(s)
    #print(20 * '\r\n')

    # 2) Парсим бинарный файл planner.rsf
    #struct_with_values = parse_planner_rsf(struct)
    #for s in struct_with_values: print(s)

    # 3) Парсим весь бинарник, цикл по кадрам
    frame = parse_by_frames()
    for f in range (frame[0]):
        print('FRAME № %s\r\n' % f)
        struct = parse_planner_stn(frame[1], frame[2])
        for s in struct: print(s)
        print(5 * '\r\n')

        struct_with_values = parse_planner_rsf(struct)
        for s in struct_with_values: print(s)


