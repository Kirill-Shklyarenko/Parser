from struct import *
import json
import copy
import os


class TelemetryReader:
    def __init__(self, file_name: str, data_struct: list, frame_size: int, frame_number: int):
        self.file_name = file_name
        self.data_struct = data_struct
        self.frame_size = frame_size
        self.frame_number = frame_number

        self.file = self.opener()

        self.frames_count = self.frame_counter()

    def opener(self):
        with open(self.file_name, 'rb') as file:
            return file

    def header_seeker(self):
        self.file.seek(14)

    def read_frame(self) -> list:
        # frame_rate = self.frame_number * self.frame_size
        frame = copy.deepcopy(self.data_struct)

        for line in frame:
            for number, cursor in enumerate(line):
                if type(cursor) is dict:
                    number = 0
                    name = cursor.get('name')
                    cursor.clear()
                    cursor.update({'name': name,
                                   'value': massive_of_values[number]})

        for i, type_w in enumerate(massive_of_types):
            if 'WW' in type_w:
                massive_of_types[i] = 'B'  # UINT_2
            elif 'SS' in type_w:
                massive_of_types[i] = 'b'  # INT_2
            elif 'UU' in type_w:
                massive_of_types[i] = 'hh'
                # size = 4  # Размер 4 байта потому что используется 2 слова х 2 байта идущие друг за другом
            elif 'LL' in type_w:
                massive_of_types[i] = ''
                # size = 4  # Размер 4 байта потому что используется 2 слова х 2 байта идущие друг за другом
            elif 'RR' in type_w:
                massive_of_types[i] = 'c'  # битовая переменная
                # size = 1  # Размер 1 байт
            elif 'FF' in type_w:
                massive_of_types[i] = 'f'
                # size = 4  # 2 слова х 2 байта(размер слова)
            massive_of_types.insert(0, '<')


            frame = file.read(len(massive_of_types))
                        massive_of_values = unpack(massive_of_types, frame)[0]




    def frame_counter(self) -> int:
        file_size = os.path.getsize(self.file_name) - 14  # Размер файла в байтах # отсекаем 14 байт заголовка
        try:
            frames_count = file_size / (self.frame_size * 2)
        except ZeroDivisionError as e:
            print(frames_count)
            print(e)
        else:
            frames_count = int(frames_count)
        return frames_count

        # word = file.read(size)
        # value = unpack(type_w, word)[0]

    def read_start_frame(file_name: str, frame_number=None):
        if file_name.is_file():
            if frame_number:
                prev_frame_number = {'prev_frame_number': frame_number - 1}
                with open(file_name, 'w') as fr_c:
                    fr_c.write(json.dumps(prev_frame_number))
            else:
                prev_frame_number = {'prev_frame_number': 0}
                with open(file_name) as fr_c:
                    prev_frame_number.update(json.load(fr_c))
            return prev_frame_number['prev_frame_number']

        else:
            prev_frame_number = {'prev_frame_number': 0}
            with open(file_name, 'w+') as fr_c:
                fr_c.write(json.dumps(prev_frame_number))
            return prev_frame_number['prev_frame_number']