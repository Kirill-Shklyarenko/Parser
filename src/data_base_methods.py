from unittest.test.testmock.testpatch import function

import psycopg2
import re
import logging as log


def change_name_of_binary_data(func: function) -> function:
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        for i in result:
            i['beamAzimuth'] = i.pop('betaBSK')
            i['beamElevation'] = i.pop('epsilonBSK')
            if 'isFake' in i:
                v = bool(i.get('isFake'))
                i.update({'isFake': v})
        return result

    return wrapper


# def adjust_to_col_names(func: function) -> function:
#     def wrapper(*args, **kwargs):
#         data = {}
#         res = []
#         result = func(*args, **kwargs)
#         columns_names = ["taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
#                          "threshold", "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
#                          "upperDistanceTrim", "beamAzimuth", "beamElevation"]
#         for i in result:
#             data.update({key: value for key, value in i.items() if key in columns_names})
#             res.append(data)
#         return res
#
#     return wrapper


class DataBase:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.cur = self.connection()

    def connection(self) -> any:
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        cur = conn.cursor()
        return cur

    def insert_to(self, table_name: str, z: dict):
        # Для того чтобы узнать имена полей таблицы
        self.cur.execute(f'SELECT * FROM "{table_name}";')
        col_names = []
        for elt in self.cur.description:
            col_names.append(elt[0])
        data = [[k, v] for k, v in z.items() if k in col_names]
        # формирование строки запроса
        columns = ','.join([f'"{x[0]}"' for x in data])
        param_placeholders = ','.join(['%s' for x in range(len(data))])
        query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({param_placeholders})'
        param_values = tuple(x[1] for x in data)
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            log.exception(f'\r\nException: {e}')
            # print(f'\r\nException: {e}')
        else:
            log.warning(f'INSERT INTO "{table_name}" {data}')
            # pprint.pprint(f'INSERT INTO "{table_name}" {data}')

    def read_from(self, table_name: str, dict_for_get_pk: dict) -> any:
        data = {}
        # data.update({key: value for key, value in z.items() if key in fields})
        # формирование строки запроса
        columns = ','.join([f'"{x}"' for x in dict_for_get_pk])
        param_placeholders = ','.join(['%s' for x in range(len(dict_for_get_pk))])
        query = f'SELECT * FROM "{table_name}" WHERE ({columns}) = ({param_placeholders})'
        param_values = tuple(x for x in dict_for_get_pk.values())
        try:
            self.cur.execute(query, param_values)
        except Exception as e:
            log.exception(f'\r\nException: {e}')
        else:
            db_values = self.cur.fetchall()
            if db_values:
                return db_values[0]
            else:
                return None

    def get_pk(self, table_name: str, pk_name: str, dict_for_get_pk: dict):
        # columns_names = []
        # data = {}
        # pk_name = ''
        # if table_name is 'BeamTasks':
            # columns_names = ["taskId", "isFake", "trackId", "taskType", "viewDirectionId", "antennaId", "pulsePeriod",
            #                  "threshold", "lowerVelocityTrim", "upperVelocityTrim", "lowerDistanceTrim",
            #                  "upperDistanceTrim", "beamAzimuth", "beamElevation"]
            # pk_name = 'BeamTask'
        # elif table_name is 'PrimaryMarks':
            # columns_names = ["BeamTask", "PrimaryMark", "primaryMarkId", "scanTime", "azimuth", "elevation",
            #                  "markType", "distance", "dopplerSpeed", "signalLevel", "reflectedEnergy",
            #                  "antennaId", "taskType", "beamAzimuth", "beamElevation"]
            # pk_name = 'PrimaryMark'
        # data.update({key: value for key, value in z.items() if key in columns_names})
        data_with_pk = self.read_from(table_name, dict_for_get_pk)
        if data_with_pk:
            # log.debug(f'{pk_name} : {data_with_pk[0]}')
            # dict_for_get_pk.update({pk_name: data_with_pk[0]})
            return {pk_name: data_with_pk[0]}
        else:
            log.debug(f'get_pk data is None')
            return None

class FrameHandler(DataBase):
    def __init__(self, frame, dsn: str):
        super().__init__(dsn)
        self.frame = frame
        self.obj = {}

    # @adjust_to_col_names
    @change_name_of_binary_data
    def beam_task(self):
        container = []
        task = {}
        for index, group in enumerate(self.frame):
            if re.search(r'\bTask\b', group[0]):
                group.pop(0)
                for c in group:
                    task.update(c)
                    log.info(f'taskId = {task["taskId"]}')
            elif re.search(r'beamTask', group[0]):
                group.pop(0)
                beam_task = {}
                beam_task.update(task)
                for c in group:
                    beam_task.update(c)
                log.info(f'TaskType = {beam_task["taskType"]}')
                self.frame = self.frame[index:]
                container.append(beam_task)
                self.obj = container
        return container

    def primary_mark(self):
        container = []
        scan_data = {'primaryMarksCount': 0}
        primary_marks_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'scanData', group[0]):
                group.pop(0)
                scan_data = {}
                for c in group:
                    scan_data.update(c)
                log.info(f'primaryMarksCount = {scan_data["primaryMarksCount"]}')
                self.frame = self.frame[index:]
            elif primary_marks_count < scan_data['primaryMarksCount']:
                if re.search(r'primaryMark', group[0]):
                    group.pop(0)
                    primary_mark = {}
                    for c in group:
                        primary_mark.update(c)

                    primary_mark.update(scan_data)
                    container.append(primary_mark)
                    primary_marks_size = scan_data['primaryMarksCount']
                    primary_marks_count += 1
                    log.info(f'primaryMarksCount == {primary_marks_count} / {primary_marks_size}')
                    log.info(f'markType = {primary_mark["type"]}')
                    self.obj = container

        return container

    def candidate(self):
        container = []
        track_candidate = {'state': 0}
        candidate_q = {'candidatesQueueSize': 0}
        candidates_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'TrackCandidates', group[0]):
                group.pop(0)
                candidate_q = {}
                for c in group:
                    candidate_q.update(c)
                log.info(f'candidatesQueueSize = {candidate_q["candidatesQueueSize"]}')
                self.frame = self.frame[index:]
            elif candidates_count < candidate_q['candidatesQueueSize']:
                if re.search(r'trackCandidate', group[0]):
                    group.pop(0)
                    track_candidate = {}
                    for c in group:
                        track_candidate.update(c)

                elif re.search(r'viewSpot', group[0]):
                    group.pop(0)
                    view_spot = {}
                    for c in group:
                        view_spot.update(c)

                elif re.search(r'distanceResolutionSpot', group[0]):
                    group.pop(0)
                    distance_res_spot = {}
                    for c in group:
                        distance_res_spot.update(c)

                elif re.search(r'velocityResolutionSpot', group[0]):
                    candidates_queue_size = candidate_q['candidatesQueueSize']
                    group.pop(0)
                    velocity_res_spot = {}
                    for c in group:
                        velocity_res_spot.update(c)
                    candidates_count += 1

                    log.info(f'candidatesQueueSize == {candidates_count} / {candidates_queue_size}')
                    log.info(f'c_state = {track_candidate["state"]}')

                    # ---------------------------ЗАПОЛНЯЕМ "Candidates"-------------------------------- #
                    candidates_ids = {}
                    candidates_ids.update({'id': track_candidate['id']})
                    container.append(candidates_ids)

                    # Проверка существует ли запись с такими параметрами
                    # candidates_ids = data_base.prepare_data_for_db('Candidates', candidates_ids)
                    # candidates_pk = data_base.read_from('Candidates', candidates_ids, ['id'])
                    # if candidates_pk is None:
                    #     data_base.insert_to('Candidates', candidates_ids)

                    candidates = {}
                    # -----------------------------------state == 0------------------------------------ #
                    if track_candidate['state'] == 0 or track_candidate['state'] == 3 or track_candidate['state'] == 5:
                        breakpoint()
                    # -----------------------------------state == 1------------------------------------ #
                    elif track_candidate['state'] == 1:  # frame 2687
                        candidates.update(view_spot)
                        container.append(candidates)
                        # except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                        # candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                        # query_for_bt = ['taskId',
                        #                 'antennaId',
                        #                 'pulsePeriod'
                        #                 ]
                        # bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
                        # if bt_pk:
                        #     candidates.update({'BeamTask': bt_pk['BeamTask']})
                        #     candidates['betaBSK'] = candidates.pop('beamAzimuth')
                        #     candidates['epsilonBSK'] = candidates.pop('beamElevation')
                            query_for_pm = ['BeamTask',
                                            'azimuth', 'elevation',
                                            # 'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
                                    candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        data_base.insert_to('CandidatesHistory', candidates)
                    # -----------------------------------state == 2------------------------------------ #
                    elif track_candidate['state'] == 2:  # frame 2689
                        candidates.update(distance_res_spot)
                        container.append(candidates)
                        except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                        candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                        query_for_bt = ['taskId',
                                        'antennaId',
                                        'threshold',
                                        'pulsePeriod'
                                        ]
                        bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates['betaBSK'] = candidates.pop('beamAzimuth')
                            candidates['epsilonBSK'] = candidates.pop('beamElevation')
                            query_for_pm = ['BeamTask',
                                            'azimuth', 'elevation',
                                            'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
                                    candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        data_base.insert_to('CandidatesHistory', candidates)
                    # -----------------------------------state == 4------------------------------------ # 4866
                    elif track_candidate['state'] == 4:
                        candidates.update(velocity_res_spot)
                        container.append(candidates)
                        except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                        candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                        query_for_bt = ['taskId',
                                        'antennaId',
                                        'threshold',
                                        'pulsePeriod'
                                        ]
                        bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates['betaBSK'] = candidates.pop('beamAzimuth')
                            candidates['epsilonBSK'] = candidates.pop('beamElevation')
                            query_for_pm = ['BeamTask',
                                            'azimuth', 'elevation',
                                            # 'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
                                    candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        data_base.insert_to('CandidatesHistory', candidates)
        self.obj = container
        return container
    def __iter__(self):
        return self.obj[0]

    def __next__(self):
        try:
            result = self.obj()[0]
        except IndexError:
            raise StopIteration

        self.obj = self.obj[1:]
        return result

    # @staticmethod
    # def map_values(data: dict) -> dict:
    #     z = []
    #     returned_data = {}
    #     for k, v in data.items():
    #         if 'isFake' in k:
    #             data['isFake'] = bool(v)
    #             if data['isFake']:
    #                 raise Exception
    #         elif 'processingTime' in k:
    #             returned_data['scanTime'] = data['processingTime']
    #         elif 'distancePeriod' in k:
    #             returned_data['distanceZoneWeight'] = data['distancePeriod']
    #         elif 'velocityPeriod' in k:
    #             returned_data['velocityZoneWeight'] = data['velocityPeriod']
    #         elif 'betaBSK' in k:
    #             returned_data['beamAzimuth'] = data['betaBSK']
    #         elif 'epsilonBSK' in k:
    #             returned_data['beamElevation'] = data['epsilonBSK']
    #         elif 'type' in k:
    #             returned_data['markType'] = data['type']
    #         elif re.search(r'\bdistance\b', k):
    #             returned_data['numDistanceZone'] = data['resolvedDistance']
    #         elif re.search(r'\bvelocity\b', k):
    #             returned_data['numVelocityZone'] = data['resolvedVelocity']
    #         elif 'possiblePeriod[' in k:
    #             z.append(v)
    #         elif 'scanPeriodSeconds' in k:
    #             returned_data['scanPeriod'] = data['scanPeriodSeconds']
    #         elif 'nextUpdateTimeSeconds' in k:
    #             returned_data['nextTimeUpdate'] = data['nextUpdateTimeSeconds']
    #         elif 'creationTimeSeconds' in k:
    #             returned_data['nextTimeUpdate'] = data['creationTimeSeconds']
    #
    #     if len(z) == 6:
    #         returned_data.update({'possiblePeriods': z})
    #     data.pop('betaBSK')
    #     data.pop('epsilonBSK')
    #     returned_data.update(data)
    #     return returned_data
