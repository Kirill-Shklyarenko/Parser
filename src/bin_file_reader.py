from struct import *
import copy
import os

planner_RSF = r'../data/Planner.rsf'


def byte_reader(type_w: str, offset: int) -> any:
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


def parse_bin_file(data: list, frame_size: int, frame_number: int) -> list:
    data_with_values = copy.deepcopy(data)
    frame_rate = frame_number * frame_size
    for line in data_with_values:
        for i in line:
            if type(i) is dict:
                name = i.get('name')
                type_w = i.get('type')
                offset = i.get('offset')
                value = byte_reader(type_w, offset + frame_rate)
                i.clear()
                i.update({name: value})
    return data_with_values


def frame_counter(frame_size: int) -> int:
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
