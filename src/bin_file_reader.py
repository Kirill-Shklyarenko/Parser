from struct import *
from pathlib import Path
import copy
import os

frame_rate_file = Path(r'../data/session_00/frame_rate')


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
    if frame_rate_file.is_file():
        with open(frame_rate_file, 'a+') as fr_c:
            try:
                old_frame_number = fr_c.readline(1)
            except Exception as e:
                fr_c.truncate(0)
                fr_c.write(f'{frame_number}')
                old_frame_number = frame_number
            else:
                fr_c.truncate(0)
                fr_c.write(str(frame_number))

    else:
        with open(frame_rate_file, 'w+') as fr_c:
            fr_c.write(f'{frame_number}')

    for line in frame:
        for i in line:
            if type(i) is dict:
                name = i.get('name')
                type_w = i.get('type')
                offset = i.get('offset')
                value = byte_reader(file_name, type_w, offset + frame_rate)
                i.clear()
                i.update({name: value})
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
