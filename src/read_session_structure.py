import copy

import logging.config

log = logging.getLogger('StructureLogger')


class StructureSessionContainer:
    __slots__ = ('frame_size', 'structure')

    def __init__(self):
        self.frame_size: int = 0
        self.structure: list = []


def read_session_structure(file_name: str) -> StructureSessionContainer:
    lines = read_lines(file_name)
    structure = StructureSessionContainer()
    structure.structure, structure.frame_size = parse_text_file(lines)
    return structure


def read_lines(file_name: str) -> list:
    with open(file_name) as file:
        data = file.readlines()
    return data


def parse_text_file(lines):
    frame_size = 0
    index = 0
    structure = []  # список элементов [0, 1, 2]
    substring = []  # элемент содержит str "NavigationData"[0] & dict "Parameters"[1]

    for i, line in enumerate(lines):
        line = line.split()
        # Поиск размера блока данных
        if len(line) == 1 and ';' not in line[0]:
            next_line = lines[i + 1].split()
            if len(next_line) == 1 and ';' not in next_line[0]:
                frame_size = int(line[0])

        # Поиск имени группы
        elif ';' in line[0]:
            next_line = lines[i + 1].split()
            if ';' not in next_line[0]:
                if substring:
                    structure.append(copy.copy(substring))
                    substring.clear()
                line.remove(';')
                newline = ''.join(line)
                substring.append(newline)
            else:
                structure.append(copy.copy(substring))
                substring.clear()
        # Поиск описания переменных
        elif len(line) > 4:
            if 'UU' in line[5]:
                params = {
                    'name': line[0],
                    'type': line[5],
                    'offset': int(line[1]) - 1,
                    'index': index
                }
                index += 1
                substring.append(params)
            elif 'LL' in line[5]:
                params = {
                    'name': line[0],
                    'type': line[5],
                    'offset': int(line[1]) - 1,
                    'index': index
                }
                index += 1
                substring.append(params)
            else:
                params = {
                    'name': line[0],
                    'type': line[5],
                    'offset': int(line[1]),
                    'index': index
                }
                index += 1
                substring.append(params)
    structure.append(substring)
    log.debug('\r'.join(map(str, structure)))
    return structure, frame_size
