
class Data_structure:
        def __init__(self):
            self.file = self.open()
            self.frame_size = self.find_frame_size()
            self.frames_count = self.find_count_of_frames()
            self.data_structure = self.do_structure()

        @staticmethod
        def open():
            with open(planner) as file:
                data = file.readlines()
                return data

        def find_count_of_frames(self):
            file_size = os.path.getsize(planner_RSF)  # Размер файла в байтах
            file_size = file_size - 14  # отсекаем 14 байт заголовка
            try:
                frames_count = file_size / (self.frame_size * 2)
            except ZeroDivisionError as e:
                print(frames_count)
                print(e)
            else:
                return int(frames_count)

        def do_structure(self):
            group = []
            substring = []  # список содержит имя "NavigationData"[0] и словарь "Parameters"[1]

            for i, line in enumerate(self.file):
                line = line.split()

                # Поиск имени группы
                if ';' in line[0]:
                    next_line = self.file[i + 1].split()
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
            return group

        def find_frame_size(self):
            # Поиск размера блока данных
            for i, line in enumerate(self.file):
                if i >= 1:
                    break
                line = line.split()
                return int(line[0])


    class Parsed_data(Data_structure):
        def __init__(self, frame_number):
            Data_structure.__init__(self)
            self.frame_number = frame_number
            self.data = self.parse_bin_file()

        def parse_bin_file(self):
            data_with_values = copy.deepcopy(self.data_structure)
            frame_rate = self.frame_number * self.frame_size
            for index, line in enumerate(data_with_values):
                for i in line:
                    if type(i) == dict:
                        type_w = i.get('type')
                        offset = i.get('offset')
                        value = byte_reader(type_w, offset)
                        i.pop('type')
                        i.pop('offset')
                        i.update({'value': value})
            return data_with_values

        def find(self, name_to_find):
            finded_data = []
            for group in self.data:
                name = group[0]
                if re.search(name_to_find, name):
                    finded_data.append(group)
            return finded_data

        def insert_to_bd(self):
            pass




# ALTER SEQUENCE "Candidates_Candidate_seq" restart with 1;

# SELECT DISTINCT "taskId", "taskType", "antennaId"
# FROM public."BeamTasks"
# ORDER BY "taskId"
# ;


# SELECT "BeamTask", "taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
# threshold, "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim", "upperDistanceTrim", "betaBSK",
# "epsilonBSK"
# FROM public."BeamTasks"
# where "trackId" != 0
# ;


# SELECT "BeamTask", "taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId",
# "pulsePeriod", threshold, "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
# "upperDistanceTrim", "betaBSK", "epsilonBSK"
# FROM public."BeamTasks"
# where "taskType" != 0
# and "taskType" != 1
# ;


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