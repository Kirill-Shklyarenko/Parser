from struct import *
import copy
import os
import re
import logging as log
from pprint import pformat, pprint


class TelemetryReader:
    def __init__(self, file_name: str, data_struct: object):
        self.file_name = file_name
        self.data_struct = data_struct.__dict__['data_struct']
        self.frame_size = data_struct.__dict__['frame_size']
        self.buff_size = (self.frame_size * 2) - 2  # 1 frame = 15444bytes   need 15428

        self.frame_number = 2600
        self.frames_range = self.frame_counter()
        self.serialize_string = self.create_serialize_string()
        # self.buffer = self.open()

    def open(self):
        with open(self.file_name, 'rb') as file:
            frame_rate = self.frame_number * (self.frame_size * 2)
            buffer = file.read(self.buff_size + frame_rate)
            buffer = buffer[frame_rate:]
            buffer = buffer[:self.buff_size]
            buffer = buffer[14:]
        return buffer

    def frame_counter(self) -> int:
        file_size = os.path.getsize(self.file_name) - 14  # Размер файла в байтах # отсекаем 14 байт заголовка
        frames_count = 0
        try:
            frames_count = file_size / (self.frame_size * 2)
        except ZeroDivisionError as e:
            log.exception(f'{frames_count}')
            log.exception(f'{e}')
        finally:
            log.info(f'frames_count = {int(frames_count)}')
            return int(frames_count)

    def create_serialize_string(self) -> str:
        serialize_string = '='
        for line in self.data_struct:
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
                    elif 'RR' in c['type']:
                        serialize_string += 'c'  # char
                    elif 'FF' in c['type']:
                        serialize_string += 'f'  # float_4
        return serialize_string

    def read_frame(self) -> list:
        frame_values = None
        try:
            frame_values = list(unpack(self.serialize_string, self.open()))
        except Exception as e:
            log.exception(f'Exception: {e}')
        finally:
            log.info(f'----------------------FRAME {self.frame_number}-----------------------')
            # print(f"\r\n\r\n\r\n--------------- FRAME № {self.frame_number} ---------------")
            frame = copy.deepcopy(self.data_struct)
            group_names = []
            for number, line in enumerate(frame):
                group_names.append(line[0])
                for cursor in line:
                    if type(cursor) is dict:
                        key = cursor.get('name')
                        cursor.clear()
                        value = frame_values[0]
                        frame_values.pop(0)
                        cursor.update({key: value})
            # formatted = pformat(frame, width=105, compact=True)
            # for line in formatted.splitlines():
            #     log.info(line.rstrip())
        return frame[2:]

    def __iter__(self):
        return self

    def __next__(self):
        try:
            result = self.read_frame()
        except IndexError:
            raise StopIteration
        self.frame_number += 1
        return result


class FrameHandler:
    def __init__(self, frame):
        self.frame = frame

    def beam_task(self):
        container = []
        task = {}
        for index, group in enumerate(self.frame):
            if re.search(r'\bTask\b', group[0]):
                for c in group[1:]:
                    task.update(c)
                self.frame = self.frame[1:]
            elif re.search(r'beamTask', group[0]):
                beam_task = {}
                beam_task.update(task)
                for c in group[1:]:
                    beam_task.update(c)
                # log.info(f'TaskType = {beam_task["taskType"]}')
                container.append(beam_task)
                self.frame = self.frame[1:]
                if len(container) == 4:
                    break
        return container

    def primary_mark(self):
        container = []
        scan_data = {'primaryMarksCount': 0}
        primary_marks_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'scanData', group[0]):
                scan_data = {}
                for c in group[1:]:
                    scan_data.update(c)
                # if scan_data["primaryMarksCount"] == 0:
                #     log.info(f'primaryMarksCount = {scan_data["primaryMarksCount"]}')
                # self.frame = self.frame[1:]
                # scan_data = {'primaryMarksCount': 10}
            elif primary_marks_count < scan_data['primaryMarksCount']:
                primary_marks_count += 1
                log.debug(f'primaryMarksCount == {primary_marks_count} / {scan_data["primaryMarksCount"]}')
                if re.search(r'primaryMark', group[0]):
                    primary_mark = {}
                    for c in group[1:]:
                        primary_mark.update(c)
                    primary_mark.update(scan_data)
                    container.append(primary_mark)
                    log.debug(f'markType = {primary_mark["type"]}')
                    self.frame = self.frame[index + 1:]
            elif re.search(r'TrackCandidates', group[0]):
                break
        return container

    def candidate(self):
        container = []
        track_candidate = {'state': 0}
        candidate_q = {'candidatesQueueSize': 0}
        candidates_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'TrackCandidates', group[0]):
                candidate_q = {}
                for c in group[1:]:
                    candidate_q.update(c)
                if candidate_q["candidatesQueueSize"] == 0:
                    log.info(f'candidatesQueueSize = {candidate_q["candidatesQueueSize"]}')
                self.frame = self.frame[1:]
                # candidate_q = {'candidatesQueueSize': 4}
            elif candidates_count < candidate_q['candidatesQueueSize']:
                breakpoint()
                if re.search(r'trackCandidate', group[0]):
                    track_candidate = {}
                    for c in group[1:]:
                        track_candidate.update(c)
                elif track_candidate['state'] == 0:
                    if re.search(r'viewSpot', group[0]):
                        view_spot = {}
                        for c in group[1:]:
                            view_spot.update(c)
                        track_candidate.update(view_spot)
                        container.append(track_candidate)
                        candidates_count += 1
                        log.info(f'candidatesQueueSize = {candidates_count} / {candidate_q["candidatesQueueSize"]}')
                        log.info(f'candidate state = {track_candidate["state"]}')
                        break
                elif track_candidate['state'] == 2:
                    if re.search(r'distanceResolutionSpot', group[0]):
                        distance_res_spot = {}
                        for c in group[1:]:
                            distance_res_spot.update(c)
                        track_candidate.update(distance_res_spot)
                        container.append(track_candidate)
                        candidates_count += 1
                        log.info(f'candidatesQueueSize = {candidates_count} / {candidate_q["candidatesQueueSize"]}')
                        log.info(f'candidate state = {track_candidate["state"]}')
                        break
                elif track_candidate['state'] == 4:
                    if re.search(r'velocityResolutionSpot', group[0]):
                        velocity_res_spot = {}
                        for c in group[1:]:
                            velocity_res_spot.update(c)
                        track_candidate.update(velocity_res_spot)
                        container.append(track_candidate)
                        candidates_count += 1
                        log.warning(f'candidatesQueueSize = {candidates_count} / {candidate_q["candidatesQueueSize"]}')
                        log.debug(f'candidate state = {track_candidate["state"]}')
                        break
            else:
                self.frame = self.frame[1:]
                break
        return container

    def air_track(self):
        container = []
        tracks_q = {'tracksQueuesSize': 0}
        tracks_count = 0
        for index, group in enumerate(self.frame):
            if type(group[0]) is not str:
                breakpoint()
            if re.search(r'\bTracks\b', group[0]):
                tracks_q = {}
                for c in group[1:]:
                    tracks_q.update(c)
                if tracks_q["tracksQueuesSize"] != 0:
                    log.warning(f'tracksQueuesSize = {tracks_q["tracksQueuesSize"]}')
                else:
                    log.info(f'tracksQueuesSize = {tracks_q["tracksQueuesSize"]}')
                self.frame = self.frame[index:]
                # tracks_q = {'tracksQueuesSize': 4}
            elif tracks_count < tracks_q['tracksQueuesSize']:
                if re.search('track_', group[0]):
                    track = {}
                    for c in group[1:]:
                        track.update(c)
                    container.append(track)
                    tracks_count += 1
                    log.info(f'track = {tracks_count} / {tracks_q["tracksQueuesSize"]}')
                    log.info(f'track_type  = {track["type"]}')
                    if track["type"] != 0:
                        log.warning(f'track_type  = {track["type"]}')
                    if tracks_count == tracks_q['tracksQueuesSize']:
                        break
        return container

    def __iter__(self):
        return self  # .obj[:self.entity_counter]

    def __next__(self):
        try:
            result = self.obj
        except IndexError:
            raise StopIteration
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
