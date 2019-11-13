from struct import *

import copy
import os
frame_rate_file = r'../data/session_00/frame_rate'


def byte_reader(file_name: str, type_w: str, offset: int) -> any:
    with open(file_name, 'rb') as file:
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


def parse_bin_file(file_name: str, data_struct: list, frame_size: int, frame_number: int) -> list:
    frame = copy.deepcopy(data_struct)
    frame_rate = frame_number * frame_size

    massive_of_types = []
    for line in frame:
        for i in line:
            if type(i) is dict:
                # name = i.get('name')
                type_w = i.get('type')
                # offset = i.get('offset')
                # value = byte_reader(file_name, type_w, offset + frame_rate)
                # i.clear()
                # i.update({name: value})
                massive_of_types.append(type_w)

    for i, type_w in enumerate(massive_of_types):
        if 'WW' in type_w:
            massive_of_types[i] = 'B'  # UINT_2
        elif 'SS' in type_w:
            massive_of_types[i] = 'b'  # INT_2
        elif 'UU' in type_w:
            massive_of_types[i] = 'h'
            # size = 4  # Размер 4 байта потому что используется 2 слова х 2 байта идущие друг за другом
        elif 'LL' in type_w:
            massive_of_types[i] = 'i'
            # size = 4  # Размер 4 байта потому что используется 2 слова х 2 байта идущие друг за другом
        elif 'RR' in type_w:
            massive_of_types[i] = 'c'  # битовая переменная
            # size = 1  # Размер 1 байт
        elif 'FF' in type_w:
            massive_of_types[i] = 'f'
            # size = 4  # 2 слова х 2 байта(размер слова)
    massive_of_types.insert(0, '<')
    with open(frame_rate_file, 'r+', encoding='UTF-8') as fr_c:
        try:
            old_frame_rate = int(fr_c.read())
        except:
            fr_c.write(str(frame_rate) + '\r\n')
            old_frame_rate = frame_rate
        fr_c.close()
    if frame_rate == old_frame_rate:
        with open(file_name, 'rb') as file:
            file.seek(14)  # отсечь Имя файла заголовка
            file.seek(frame_rate)
            file = file.read()
            with open(file_name + 's', 'wb') as new_file:
                new_file.write(bytes(file))
            with open(file_name + 's', 'rb') as new_file:

                frame = new_file.read(len(massive_of_types))
                asd = ''.join(massive_of_types)
                massive_of_values = unpack(asd, frame)[0]

                for line in frame:
                    for number, cursor in enumerate(line):
                        if type(cursor) is dict:
                            number = 0
                            name = cursor.get('name')
                            cursor.clear()
                            cursor.update({'name': name,
                                           'value': massive_of_values[number]})

    elif frame_rate < old_frame_rate:
        with open(file_name, 'rb') as file:
            file.seek(14)  # отсечь Имя файла заголовка
            file.seek(frame_rate)
            frame = file.read(len(massive_of_types))
            massive_of_values = unpack(massive_of_types, frame)[0]

            for line in frame:
                for number, cursor in enumerate(line):
                    if type(cursor) is dict:
                        number = 0
                        name = cursor.get('name')
                        cursor.clear()
                        cursor.update({'name': name,
                                       'value': massive_of_values[number]})
    else:
        with open(file_name + 's', 'rb') as file:
            file.seek(14)  # отсечь Имя файла заголовка
            file.seek(frame_rate)
            frame = file.read(len(massive_of_types))
            massive_of_values = unpack(massive_of_types, frame)[0]

            for line in frame:
                for number, cursor in enumerate(line):
                    if type(cursor) is dict:
                        number = 0
                        name = cursor.get('name')
                        cursor.clear()
                        cursor.update({'name': name,
                                       'value': massive_of_values[number]})


    return frame


def frame_counter(file_name: str, frame_size: int) -> int:
    file_size = os.path.getsize(file_name) - 14  # Размер файла в байтах # отсекаем 14 байт заголовка
    try:
        frames_count = file_size / (frame_size * 2)
    except ZeroDivisionError as e:
        print(frames_count)
        print(e)
    else:
        frames_count = int(frames_count)
    return frames_count
