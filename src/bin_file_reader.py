from struct import *
import json
import copy
import os
import sys


class TelemetryReader:
    def __init__(self, file_name_str: str, data_struct: list, frame_size: int, frame_rate_file: str):
        self.file_name_str = file_name_str
        self.data_struct = data_struct
        self.frame_size = frame_size
        self.frame_rate_file = frame_rate_file

        self.start_frame = self.read_start_frame()
        self.frames_count = self.frame_counter()

    def write_start_frame(self, frame_number):
        if self.frame_rate_file.is_file():
            prev_frame_number = {'prev_frame_number': frame_number - 1}
            with open(self.frame_rate_file, 'w') as fr_c:
                fr_c.write(json.dumps(prev_frame_number))
            return prev_frame_number['prev_frame_number']
        else:
            prev_frame_number = {'prev_frame_number': frame_number - 1}
            with open(self.frame_rate_file, 'w+') as fr_c:
                fr_c.write(json.dumps(prev_frame_number))
            return prev_frame_number['prev_frame_number']

    def read_start_frame(self):
        if self.frame_rate_file.is_file():
            prev_frame_number = {'prev_frame_number': 0}
            with open(self.frame_rate_file) as fr_c:
                prev_frame_number.update(json.load(fr_c))
            return prev_frame_number['prev_frame_number']

        else:
            prev_frame_number = {'prev_frame_number': 0}
            with open(self.frame_rate_file, 'w+') as fr_c:
                fr_c.write(json.dumps(prev_frame_number))
            return prev_frame_number['prev_frame_number']

    def frame_counter(self) -> int:
        file_size = os.path.getsize(self.file_name_str) - 14  # Размер файла в байтах # отсекаем 14 байт заголовка
        frames_count = 0
        try:
            frames_count = file_size / (self.frame_size * 2)
        except ZeroDivisionError as e:
            print(frames_count)
            print(e)
        finally:
            return int(frames_count)

    def create_serialize_string(self) -> str:
        serialize_string = '='
        for line in self.data_struct:
            for c in line:
                if type(c) is dict:
                    if 'WW' in c['type']:  # UINT_2 # "<"  little-endian
                        serialize_string += 'H'
                    elif 'SS' in c['type']:  # INT_2
                        serialize_string += 'h'
                    elif 'UU' in c['type']:  # INT_4
                        serialize_string += 'i'
                    elif 'LL' in c['type']:  # INT_4
                        serialize_string += 'i'
                    elif 'RR' in c['type']:
                        serialize_string += 'c'  # char
                    elif 'FF' in c['type']:
                        serialize_string += 'f'  # float_4
        return serialize_string

    def read_frame(self) -> list:
        serialize_string = self.create_serialize_string()
        buff_size = (self.frame_size * 2) - 16  # 1 frame = 15444bytes   need 15428
        with open(self.file_name_str, 'rb') as file_object:
            file_object.seek(14)
            buffer = file_object.read(buff_size)
            frame_values = list(unpack(serialize_string, buffer))
            frame = copy.deepcopy(self.data_struct)
            group_names = []
            for number, line in enumerate(frame):
                group_names.append(line[0])
                for cursor in line:
                    if type(cursor) is dict:
                        key = cursor.get('name')
                        cursor.clear()
                        value = frame_values[0]
                        frame_values.pop(0)
                        cursor.update({key: value})
        frame_size = sys.getsizeof(frame)
        return frame
