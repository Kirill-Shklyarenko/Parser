import copy
from typing import Tuple


def opener(planner: str) -> list:
    with open(planner) as file:
        data = file.readlines()
    return data


def parse_text_file(planner: str) -> Tuple[list, int]:
    frame_size = 0
    group = []  # просто список элементов [0, 1, 2]
    substring = []  # список содержит имя "NavigationData"[0] и словарь "Parameters"[1]
    file = opener(planner)

    for i, line in enumerate(file):
        line = line.split()
        # Поиск размера блока данных
        if len(line) == 1 and ';' not in line[0]:
            next_line = file[i + 1].split()
            if len(next_line) == 1 and ';' not in next_line[0]:
                frame_size = int(line[0])

        # Поиск имени группы
        elif ';' in line[0]:
            next_line = file[i + 1].split()
            if ';' not in next_line[0]:
                if substring:
                    group.append(copy.copy(substring))
                    substring.clear()
                line.remove(';')
                nwline = ''.join(line)
                substring.append(nwline)
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
    return group, frame_size
