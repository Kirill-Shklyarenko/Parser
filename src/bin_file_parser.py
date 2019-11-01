from struct import *
import copy
import os


def byte_reader(buffer: bytes, type_w: str, offset: int) -> any:
    offset *= 2
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

    word = buffer[offset: offset + size]
    value = unpack(type_w, word)[0]
    return value


def read_bin_file(data_structure: list, buffer: bytes) -> list:
    data_with_values = copy.deepcopy(data_structure)
    for line in data_with_values:
        for i in line:
            if type(i) is dict:
                name = i.get('name')
                type_w = i.get('type')
                offset = i.get('offset')
                value = byte_reader(buffer, type_w, offset)
                i.clear()
                i.update({name: value})
    return data_with_values


def frame_counter(planner_rsf_filename: str, frame_size: int) -> int:
    file_size = os.path.getsize(planner_rsf_filename)  # Размер файла в байтах
    file_size = file_size - 14  # отсекаем 14 байт заголовка
    frames_count = 0
    try:
        frames_count = file_size / (frame_size * 2)
    except ZeroDivisionError as e:
        print(frames_count)
        print(e)
    else:
        frames_count = int(frames_count)
    return frames_count
