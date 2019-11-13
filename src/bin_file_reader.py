from struct import *
import json
import copy
import os


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
            print(len(serialize_string))
            buffer = file_object.read(buff_size)
            frame_values = unpack(serialize_string, buffer)
            frame = copy.deepcopy(self.data_struct)
            dict_of_params = {}
            group_names = []
            value_names = []
            for number, line in enumerate(frame):
                group_names.append(line[0])
                for cursor in line:
                    if type(cursor) is dict:
                        value_names.append(cursor.get('name'))
                group_names.append(value_names)

            for group in group_names:
                if type(group) is list:
                    for id, val in enumerate(group):
                        dict_of_params.update({val: frame_values[id]})
                    group.clear()
                    group.append()
        return frame
