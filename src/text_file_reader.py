import copy


class StructureReader:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.file_obj = self.open()
        self.frame_size = self.find_frame_size()
        self.data_struct = self.parse_text_file()

    def open(self) -> list:
        with open(self.file_name) as file:
            data = file.readlines()
        return data

    def find_frame_size(self) -> int:
        frame_size = 0
        # Поиск размера блока данных
        for i, line in enumerate(self.file_obj):
            line = line.split()
            if i == 0:
                frame_size = int(line[0])
                self.file_obj.pop(i)
                self.file_obj.pop(i)
                break
        return frame_size

    def parse_text_file(self) -> list:
        group = []  # список элементов [0, 1, 2]
        substring = []  # элемент содержит str "NavigationData"[0] & dict "Parameters"[1]

        for i, line in enumerate(self.file_obj):
            line = line.split()
            # Поиск размера блока данных
            if len(line) == 1 and ';' not in line[0]:
                next_line = self.file_obj[i + 1].split()
                if len(next_line) == 1 and ';' not in next_line[0]:
                    frame_size = int(line[0])

            # Поиск имени группы
            elif ';' in line[0]:
                next_line = self.file_obj[i + 1].split()
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
