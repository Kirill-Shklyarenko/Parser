from struct import *
import copy
import os
import logging as log


class TelemetryReader:
    def __init__(self, file_name: str, data_struct: object):
        self.file_name_str = file_name
        self.data_struct = data_struct.__dict__['data_struct']
        self.frame_size = data_struct.__dict__['frame_size']

        self.frame_number = 0
        self.frames_count = self.frame_counter()
        self.serialize_string = self.create_serialize_string()

    # def opener(self):
    #     file = open(self.file_name_str, 'rb')
    #
    #     file.read()
    #     return file

    def frame_counter(self) -> int:
        file_size = os.path.getsize(self.file_name_str) - 14  # Размер файла в байтах # отсекаем 14 байт заголовка
        frames_count = 0
        try:
            frames_count = file_size / (self.frame_size * 2)
        except ZeroDivisionError as e:
            log.exception(f'{frames_count}')
            log.exception(f'{e}')
            # print(frames_count)
            # print(e)
        finally:
            log.info(f'frames_count = {int(frames_count)}')
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
        file = open(self.file_name_str, 'rb')

        buff_size = (self.frame_size * 2) - 2  # 1 frame = 15444bytes   need 15428
        frame_rate = self.frame_number * (self.frame_size * 2)
        buffer = file.read(buff_size + frame_rate)

        buffer = buffer[frame_rate:]
        buffer = buffer[:buff_size]
        buffer = buffer[14:]

        try:
            frame_values = list(unpack(self.serialize_string, buffer))
        except Exception as e:
            log.exception(f'\r\nException: {e}')

        print(f"\r\n\r\n\r\n--------------- FRAME № {self.frame_number} ---------------")
        log.warning(f"--------------- FRAME № {self.frame_number} ---------------")
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
        return frame

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.read_frame()
        except IndexError:
            raise StopIteration
        self.frame_number += 1
        return result
