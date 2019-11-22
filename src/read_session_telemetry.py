import copy
import logging as log
import os
from struct import unpack


class BinFrameReader:
    __slots__ = ('__file_obj', '__frame_rate', '__frame_size', '__header_size', '__frame_buffer')

    def __init__(self, file_name: str, frame_rate: int, frame_size: int, header_size=14):
        self.__file_obj = open(file_name, 'rb', 1)
        self.__frame_rate = frame_rate
        self.__frame_size = frame_size
        self.__header_size = header_size
        self.__frame_buffer = None

    def header_seeker(self) -> bytes:
        return self.__frame_buffer[self.__header_size:]

    def init_to_start(self) -> bytes:
        # обрезаем от конца(10) по сайзу -> # до 5 получаем фрейм № 2
        return self.__frame_buffer[self.__frame_rate:]

    def read_next_frame(self) -> bytes:
        # например сайз=1, # текущий фрейм № 0 -> читаем до конца 1 * 0 + 1 = 1 -> фрейм рейт (может быть = 0)
        self.__frame_buffer = self.__file_obj.read(self.__frame_rate + self.__frame_size)
        self.__frame_buffer = self.init_to_start()
        self.__frame_buffer = self.header_seeker()
        return self.__frame_buffer


class TelemetryFrameIterator(BinFrameReader):
    __slots__ = ('__data_struct', '__frame_size_in_bytes', '__frame_index', '__frame_rate',
                 '__frame_buffer', '__serialize_string', '__frames_count')

    def __init__(self, file_name: str, structure, frame_index=0):
        self.__data_struct = structure.structure
        self.__frame_size_in_bytes = structure.frame_size * 2  # need 16072 bytes
        self.__frame_index = frame_index
        self.__frame_rate = self.__frame_size_in_bytes * self.__frame_index
        self.__frame_buffer = None
        self.__serialize_string = self.create_serialize_string()
        self.__frames_count = self.frame_counter(file_name)
        super().__init__(file_name, self.__frame_rate, self.__frame_size_in_bytes)

    def create_serialize_string(self) -> str:
        serialize_string = '='
        for line in self.__data_struct:
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
                    elif 'RR' in c['type']:  # char
                        serialize_string += 'c'
                    elif 'FF' in c['type']:  # float_4
                        serialize_string += 'f'
        return serialize_string

    def frame_counter(self, file_name: str) -> int:
        file_size = os.path.getsize(file_name) - 14  # Размер файла в байтах # отсекаем 14 байт заголовка
        frames_count = 0
        try:
            frames_count = file_size / self.__frame_size_in_bytes
        except ZeroDivisionError as e:
            log.exception(f'{e} , {frames_count}')
        finally:
            log.info(f'frames_count = {int(frames_count)}')
            return int(frames_count)

    def __convert_buffer_to_values(self) -> list:
        try:
            self.__frame_buffer = self.__frame_buffer[:len(self.__frame_buffer) - 6]  # "странная" коррекция
            frame_values = list(unpack(self.__serialize_string, self.__frame_buffer))  # need 16072 bytes
            return frame_values
        except Exception as e:
            log.exception(f'Exception: {e}')
            exit()

    def __fill_session_structure(self) -> list:
        frame_values = self.__convert_buffer_to_values()
        filled_frame = copy.deepcopy(self.__data_struct)
        group_names = []
        for number, line in enumerate(filled_frame):
            group_names.append(line[0])
            for c in line:
                if type(c) is dict:
                    key = c.get('name')
                    c.clear()
                    value = frame_values[0]
                    frame_values.pop(0)
                    c.update({key: value})
        return filled_frame[2:]

    def __iter__(self):
        return self

    def __next__(self):
        self.__frame_buffer = self.read_next_frame()
        try:
            log.info(f'----------------------- FRAME {self.__frame_index} ------------------')
            result = self.__fill_session_structure()
            self.__frame_index += 1
            return result
        except IndexError:
            raise StopIteration
