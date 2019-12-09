import logging.config
import os
from struct import unpack

frame_log = logging.getLogger('FrameLogger')
console_log = logging.getLogger('simpleExample')


class BinFrameReader:
    __slots__ = ('__file_name', '__frame_size_in_bytes', '__header_size', '__file', '__frames_count', 'frame_log_flag')

    def __init__(self, file_name: str, structure, header_size=14):
        self.frame_log_flag = None
        console_log.info(f'Turn ON Frame logger?')
        console_log.info(f'ENTER "y" OR "n"')
        answer = input()
        if answer == 'y':
            self.frame_log_flag = logging.getLogger('FrameLogger')
        self.__file_name = file_name
        self.__frame_size_in_bytes = structure.frame_size * 2
        self.__header_size = header_size
        self.__file = open(self.__file_name, 'rb', 1)
        self.__frames_count = self.__frame_counter()

    def _init_to_start(self, frame_index):
        self.__file.seek(self.__frame_size_in_bytes * frame_index + self.__header_size)

    def _read_next_frame(self) -> bytes:
        return self.__file.read(self.__frame_size_in_bytes)

    def __frame_counter(self) -> int:
        file_size = os.path.getsize(self.__file_name) - self.__header_size
        frames_count = 0
        try:
            frames_count = file_size / self.__frame_size_in_bytes
        except ZeroDivisionError as e:
            console_log.exception(f'{e} , {frames_count}')
        else:
            console_log.info(f'Count of Frames = {int(frames_count)}')
            return int(frames_count)


class TelemetryFrameIterator(BinFrameReader):
    __slots__ = ('__data_struct', 'frame_index', '__frame_buffer', '__serialize_string')

    def __init__(self, file_name: str, structure, frame_index=0):
        super().__init__(file_name, structure)
        self.frame_index = frame_index
        self.__data_struct = structure.structure
        self.__frame_buffer = None
        self.__serialize_string = self.__create_serialize_string()

    def __convert_buffer_to_values(self) -> tuple:
        return unpack(self.__serialize_string, self.__frame_buffer)

    def __fill_session_structure(self) -> list:
        frame_values = self.__convert_buffer_to_values()
        return list(zip([[c for c in line if type(c) is str] for line in self.__data_struct],
                        [[{c.get('name'): frame_values[c.get('index')]} for c in line if type(c) is dict] for line in
                         self.__data_struct]))

    def __create_serialize_string(self) -> str:
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

    def __iter__(self):
        self._init_to_start(self.frame_index)
        return self

    def __next__(self):
        self.__frame_buffer = self._read_next_frame()
        if self.__frame_buffer:
            try:
                result = self.__fill_session_structure()
            except IndexError:
                raise StopIteration
            else:
                if self.frame_log_flag:
                    frame_log.debug('\r'.join(map(str, result)))
                    frame_log.info(
                        f'------------------------- FRAME {(self.frame_index / 100)} -------------------------')
                console_log.info(
                    f'------------------------- FRAME {(self.frame_index / 100)} -------------------------')
                self.frame_index += 1
                return result
        else:
            console_log.debug(f'Last frame is reached')
            raise StopIteration
