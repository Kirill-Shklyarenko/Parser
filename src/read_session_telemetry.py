import logging.config
import os
from struct import unpack

log = logging.getLogger('FrameLogger')


class BinFrameReader:
    __slots__ = ('__frame_index', '__file_name', '__file_obj', '__frame_size', '__header_size',
                 '__frame_buffer', '__frame_size_in_bytes', '__frames_count', '__frame_rate')

    def __init__(self, file_name: str, structure, header_size=14):
        self.__file_name = file_name
        self.__frame_size = structure.frame_size
        self.__header_size = header_size
        self.__frame_rate = 0
        self.__frame_buffer = None
        self.__file_obj = open(self.__file_name, 'rb', 1)
        self.__frame_size_in_bytes = self.__frame_size * 2
        self.__frames_count = self.__frame_counter()

    def init_to_start(self):
        return self.__file_obj.seek(self.__frame_rate)

    def read_next_frame(self, frame_index) -> bytes:
        self.__frame_rate = self.__frame_size_in_bytes * frame_index + self.__header_size
        self.__frame_buffer = self.init_to_start()
        self.__frame_buffer = self.__file_obj.read(self.__frame_size_in_bytes)
        if len(self.__frame_buffer) == 0:
            log.debug(f'Last frame is reached')
            raise StopIteration
        return self.__frame_buffer

    def __frame_counter(self) -> int:
        file_size = os.path.getsize(self.__file_name) - self.__header_size
        frames_count = 0
        try:
            frames_count = file_size / self.__frame_size_in_bytes
        except ZeroDivisionError as e:
            log.exception(f'{e} , {frames_count}')
        finally:
            log.info(f'frames_count = {int(frames_count)}')
            return int(frames_count)


class TelemetryFrameIterator(BinFrameReader):
    __slots__ = ('__data_struct', '__frame_index', '__serialize_string', '__frame_buffer')

    def __init__(self, file_name: str, structure, frame_index=0):
        super().__init__(file_name, structure)
        self.__data_struct = structure.structure
        self.__frame_index = frame_index
        self.__frame_buffer = None
        self.__serialize_string = self.__create_serialize_string()

    def __convert_buffer_to_values(self) -> tuple:
        try:
            frame_values = unpack(self.__serialize_string, self.__frame_buffer)
            return frame_values
        except Exception as e:
            log.exception(f'Exception: {e}')

    def __fill_session_structure(self) -> list:
        frame_values = self.__convert_buffer_to_values()
        index = 0
        filled_frame = []
        block = []
        params = {}
        for line in self.__data_struct:
            block.append(line[0])
            for c in line:
                if type(c) is dict:
                    key = c.get('name')
                    value = frame_values[index]
                    index += 1
                    params.update({key: value})
            params_to = params.copy()
            block.append(params_to)
            params.clear()
            block_to = block.copy()
            filled_frame.append(block_to)
            block.clear()
        log.debug('\r'.join(map(str, filled_frame)))
        # filled_frame = [
        #     [
        #         {c.get('name'): frame_values[c.get('index', 0)]}
        #         for c in line
        #         if type(c) is dict
        #
        #     ]
        #     for line in self.__data_struct
        # ]
        return filled_frame

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
        self.init_to_start()
        return self

    def __next__(self):
        self.__frame_buffer = self.read_next_frame(self.__frame_index)
        try:
            log.info(f'\r\n\r\n\r\n\r\n\r\n\r\n----------------------- FRAME {self.__frame_index} ------------------')
            result = self.__fill_session_structure()
            self.__frame_index += 1
            return result
        except IndexError:
            raise StopIteration
