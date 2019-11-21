import copy


class StructureSessionContainer:
    __slots__ = ['frame_size', 'structure']

    def __init__(self):
        self.frame_size: int = 0
        self.structure: list = []


def read_session_structure(file_name: str) -> StructureSessionContainer:
    lines = read_lines(file_name)
    structure = StructureSessionContainer()
    structure.frame_size = find_frame_size(lines)
    structure.structure = parse_text_file(lines)
    return structure


def read_lines(file_name: str) -> list:
    with open(file_name) as file:
        data = file.readlines()
    return data


def find_frame_size(lines) -> int:
    frame_size = 0
    # Поиск размера блока данных
    for i, line in enumerate(lines):
        line = line.split()
        if i == 0:
            frame_size = int(line[0])
            break
    return frame_size


def parse_text_file(lines) -> list:
    group = []  # список элементов [0, 1, 2]
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
                    group.append(copy.copy(substring))
                    substring.clear()
                line.remove(';')
                newline = ''.join(line)
                substring.append(newline)
            else:
                group.append(copy.copy(substring))
                substring.clear()

        # Поиск описания переменных
        elif len(line) > 3:
            if 'UU' in line[5]:
                params = {
                    'name': line[0],
                    'type': line[5],
                    'offset': int(line[1]) - 1
                }
                substring.append(params)
            elif 'LL' in line[5]:
                params = {
                    'name': line[0],
                    'type': line[5],
                    'offset': int(line[1]) - 1
                }
                substring.append(params)
            else:
                params = {
                    'name': line[0],
                    'type': line[5],
                    'offset': int(line[1])
                }
                substring.append(params)
    return group
