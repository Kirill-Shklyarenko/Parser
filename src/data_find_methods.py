import re
import copy


def create_group(data: list) -> list:
    group = []  # список элементов [000, 001, 002]
    substring = []  # который соержит имя "NavigationData, Flags, Beamtask" etc
    params = {}  # со словарем из параметров "Lon, Lat" etc
    cnt = 0
    for line in data:
        if type(line) is str:
            cnt += 1
            if cnt > 1:
                substring.append(copy.copy(params))
                params.clear()
                group.append(copy.copy(substring))
                substring.clear()
            substring.append(line)
        elif type(line) is list:
            params[line[0]] = line[1]
    return group


def entity_counter(data: list, keyword: str) -> int:
    first_string_in_match = False
    gap = False
    matches_count = 0
    entity_c = 0
    for group in data:
        name = group[0]

        if re.search(keyword, name) and matches_count == 0:
            first_string_in_match = True
            matches_count += 1
        elif re.search(keyword, name) and first_string_in_match and not gap:
            matches_count += 1
        elif re.search(keyword, name) and gap:
            gap = False
            matches_count = 0
            entity_c += 1
        elif matches_count >= 1:
            gap = True
    return entity_c + 1


def find_group(data: list, keyword: str, id=0) -> tuple:
    finded_data = []
    first_string_in_match = False
    gap = False
    matches_count = 0
    prev_id = id
    for id, group in enumerate(data):
        name = group[0]
        if id > prev_id:

            if re.search(keyword, name) and matches_count == 0:
                first_string_in_match = True
                matches_count += 1
                finded_data.append(group)
            elif re.search(keyword, name) and first_string_in_match and not gap:
                matches_count += 1
                finded_data.append(group)
            elif re.search(keyword, name) and gap:
                return finded_data, id - 2
            elif matches_count >= 1:
                gap = True
    return finded_data, id - 2


def find_item(data: list, item: list, id=0) -> list:
    finded_data = []
    names = []
    params = []
    if id:
        data = data[:id]
        data = list(reversed(data))
    for i, k in enumerate(item):
        index = i + 1
        if index % 2 == 0:
            params.append(k)
        else:
            names.append(k)

    for group in data:
        for name in names:
            if name in group[0]:
                for i in group:
                    if type(i) is dict:
                        key = [x for x in i][0]
                        for param in params:
                            if key == param:
                                finded_data.append(i)
                                if len(finded_data) == len(params):
                                    return finded_data
                            else:
                                continue


def add_to(group: list, item: list):
    for i in group:
        for val in item:
            i.append(val)
