import copy
import logging as log
import os
from functools import partial
from struct import *

from decorators import *


def binary_stream_generator(file_name, blksize):
    # raw_binary_stream = open(file_name, 'rb', 0)
    with file_name.open('rb') as raw_binary_stream:
        reader = partial(raw_binary_stream.read1, blksize)
        file_iterator = iter(reader, bytes())
        for chunk in file_iterator:
            yield chunk


def create_buffer(file_name, blksize) -> list:
    buffer = list(binary_stream_generator(file_name, blksize))
    res = []
    k = None
    for i, c in enumerate(buffer):
        if i % 2 == 0:
            k = c
        else:
            b = k + c
            res.append(b)
    return res


def frame_counter(file_name, frame_size) -> int:
    file_size = os.path.getsize(file_name) - 14  # Размер файла в байтах # отсекаем 14 байт заголовка
    frames_count = 0
    try:
        frames_count = file_size / (frame_size * 2)
    except ZeroDivisionError as e:
        log.exception(f'{e} , {frames_count}')
    finally:
        log.info(f'frames_count = {int(frames_count)}')
        return int(frames_count)


def create_serialize_string(data_struct) -> str:
    serialize_string = '='
    for line in data_struct:
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


class TelemetryFrameIterator:
    __slots__ = ('__data_struct', '__frame_size_in_bytes', '__frame_number',
                 '__raw_buffer', '__serialize_string', '__frames_count',)

    def __init__(self, file_name: str, structure):
        self.__data_struct = structure.structure
        self.__frame_size_in_bytes = (structure.frame_size * 2)  # need 16072 bytes

        self.__frame_number = 0
        self.__raw_buffer = create_buffer(file_name, self.__frame_size_in_bytes)
        self.__serialize_string = create_serialize_string(structure.structure)
        self.__frames_count = frame_counter(file_name, structure.frame_size)

    def __slice_buffer(self):
        buffer = self.__raw_buffer[self.__frame_number]
        buffer = buffer[:self.__frame_size_in_bytes - 6]
        buffer = buffer[14:]
        return buffer

    def __convert_buffer_to_values(self) -> list:
        try:
            buffer = self.__slice_buffer()
            frame_values = list(unpack(self.__serialize_string, buffer))
            return frame_values
        except Exception as e:
            log.exception(f'Exception: {e}')

    def __fill_session_structure(self) -> list:
        frame_values = self.__convert_buffer_to_values()
        filled_frame = copy.deepcopy(self.__data_struct)
        group_names = []
        for number, line in enumerate(filled_frame):
            group_names.append(line[0])
            for c in line:
                if type(c) is dict:
                    key = c.get('name')
                    c.clear()
                    value = frame_values[0]
                    frame_values.pop(0)
                    c.update({key: value})
        return filled_frame[2:]

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self.__frame_number < self.__frames_count:
                log.info(f'----------------------- FRAME {self.__frame_number} ------------------')
                result = self.__fill_session_structure()
                self.__frame_number += 1
                return result
        except IndexError:
            raise StopIteration


# def read_session_telemetry(file_name, structure):
#     raw_binary_stream = read_raw_binary_stream(file_name)
#     telemetry = TelemetryFrameIterator()
#     serialize_string = create_serialize_string(structure.structure)
#     frame_size_in_words = structure.frame_size
#     frame_size_in_bytes = (frame_size_in_words * 2) - 6  # need 16072 bytes
#     frames_count = frame_counter(file_name, frame_size_in_words)


# ----------------------- #  ----------------------- # ----------------------- # ---------------------- #
# ----------------------- #  ----------------------- # ----------------------- # ---------------------- #
# ----------------------- #  ----------------------- # ----------------------- # ---------------------- #


class DataBlocksReader:
    # __slots__ = ('frame',)

    def __init__(self, frame):
        self.frame = frame

    @mapper
    def beam_tasks(self) -> list:
        container = []
        task = {}
        beam_task = {}
        for index, group in enumerate(self.frame):
            if re.search(r'\bTask\b', group[0]):
                for c in group[1:]:
                    task.update(c)
                self.frame = self.frame[1:]
            elif re.search(r'beamTask', group[0]):
                beam_task.update(task)
                for c in group[1:]:
                    beam_task.update(c)
                c = {k: bool(v) for k, v in beam_task.items() if k == 'isFake'}
                beam_task.update(c)
                container.append(beam_task)
                self.frame = self.frame[1:]
                if len(container) == 4:
                    break
        return container

    @mapper
    def primary_marks(self) -> list:
        container = []
        primary_mark = {}
        scan_data = {'primaryMarksCount': 0}
        primary_marks_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'scanData', group[0]):
                for c in group[1:]:
                    scan_data.update(c)
            elif primary_marks_count < scan_data['primaryMarksCount']:
                if re.search(r'primaryMark', group[0]):
                    for c in group[1:]:
                        primary_mark.update(c)
                    primary_mark.update(scan_data)
                    container.append(primary_mark)
                    primary_marks_count += 1
                    # log.info(f'PrimaryMarks == {primary_marks_count} / {scan_data["primaryMarksCount"]}')
                    # log.info(f'PrimaryMark type = {primary_mark["type"]}')
                    self.frame = self.frame[index + 1:]
                    if primary_marks_count == scan_data['primaryMarksCount']:
                        self.frame = self.frame[1:]
                        break
                self.frame = self.frame[1:]
        return container

    @mapper
    def candidates(self) -> list:
        container = []
        track_candidate = {'state': 0}
        candidate_q = {'candidatesQueueSize': 0}
        candidates_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'TrackCandidates', group[0]):
                candidate_q = {}
                for c in group[1:]:
                    candidate_q.update(c)
                self.frame = self.frame[index:]
            elif candidates_count < candidate_q['candidatesQueueSize']:
                if re.search(r'trackCandidate', group[0]):
                    for c in group[1:]:
                        track_candidate.update(c)
                elif track_candidate['state'] == 1:
                    if re.search(r'viewSpot', group[0]):
                        view_spot = {}
                        for c in group[1:]:
                            view_spot.update(c)
                        track_candidate.update(view_spot)
                        container.append(track_candidate)
                        candidates_count += 1
                        # log.info(f'Candidates = {candidates_count} / {candidate_q["candidatesQueueSize"]}')
                        # log.info(f'Candidate state = {track_candidate["state"]}')
                        if candidates_count == candidate_q['candidatesQueueSize']:
                            self.frame = self.frame[1:]
                            break
                elif track_candidate['state'] == 2:
                    if re.search(r'distanceResolutionSpot', group[0]):
                        distance_res_spot = {}
                        for c in group[1:]:
                            distance_res_spot.update(c)
                        track_candidate.update(distance_res_spot)
                        track_candidate.update({'distanceZoneWidth': (track_candidate['resolvedDistance'] -
                                                                      track_candidate['distance']) / track_candidate[
                                                                         'distancePeriod']})
                        track_candidate.update({'numDistanceZone': round(track_candidate['resolvedDistance'] /
                                                                         track_candidate['distancePeriod'])})
                        container.append(track_candidate)
                        candidates_count += 1
                        # log.info(f'Candidates = {candidates_count} / {candidate_q["candidatesQueueSize"]}')
                        # log.info(f'Candidate state = {track_candidate["state"]}')
                        if candidates_count == candidate_q['candidatesQueueSize']:
                            self.frame = self.frame[1:]
                            break
                elif track_candidate['state'] == 4:
                    if re.search(r'velocityResolutionSpot', group[0]):
                        velocity_res_spot = {}
                        for c in group[1:]:
                            velocity_res_spot.update(c)
                        track_candidate.update(velocity_res_spot)
                        track_candidate.update({'distanceZoneWidth': (track_candidate['resolvedDistance'] -
                                                                      track_candidate['distance']) / track_candidate[
                                                                         'distancePeriod']})
                        track_candidate.update({'numDistanceZone': round(track_candidate['resolvedDistance'] /
                                                                         track_candidate['distancePeriod'])})
                        track_candidate.update({'velocityZoneWidth': (track_candidate['resolvedVelocity'] -
                                                                      track_candidate['velocity']) / track_candidate[
                                                                         'velocityPeriod']})
                        track_candidate.update({'numVelocityZone': round(track_candidate['resolvedVelocity'] /
                                                                         track_candidate['velocityPeriod'])})
                        container.append(track_candidate)
                        candidates_count += 1
                        # log.info(f'Candidates = {candidates_count} / {candidate_q["candidatesQueueSize"]}')
                        # log.info(f'Candidate state = {track_candidate["state"]}')
                        if candidates_count == candidate_q['candidatesQueueSize']:
                            self.frame = self.frame[1:]
                            break
                else:
                    candidates_count += 1
                    # log.info(f'Candidates = {candidates_count} / {candidate_q["candidatesQueueSize"]}')
                    # log.info(f'Candidate state = {track_candidate["state"]}')
                    if candidates_count == candidate_q['candidatesQueueSize']:
                        self.frame = self.frame[1:]
                        break
                self.frame = self.frame[1:]
        return container

    @mapper
    def air_tracks(self) -> list:
        container = []
        track = {}
        tracks_q = {'tracksQueuesSize': 0}
        tracks_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'\bTracks\b', group[0]):
                tracks_q = {}
                for c in group[1:]:
                    tracks_q.update(c)
                # if tracks_q["tracksQueuesSize"] != 0:
                #     log.info(f'tracksQueuesSize = {tracks_q["tracksQueuesSize"]}')
                # else:
                #     log.info(f'tracksQueuesSize = {tracks_q["tracksQueuesSize"]}')
                self.frame = self.frame[index:]
            elif tracks_count < tracks_q['tracksQueuesSize']:
                if re.search('track_', group[0]):
                    for c in group[1:]:
                        track.update(c)
                    container.append(track)
                    tracks_count += 1
                    # log.info(f'Tracks = {tracks_count} / {tracks_q["tracksQueuesSize"]}')
                    # log.info(f'Track type  = {track["type"]}')
                    if track["type"] != 0:
                        log.warning(f'type  = {track["type"]}')
                    if tracks_count == tracks_q['tracksQueuesSize']:
                        break
            self.frame = self.frame[1:]
        return container

    def air_marks_misses(self) -> list:
        container = []
        air_marks = {}
        misses_count = {'AirMarksMissesCount': 0}
        marks_misses_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'AirMarksMisses', group[0]):
                for c in group[1:]:
                    misses_count.update(c)
                self.frame = self.frame[index:]
            elif marks_misses_count < misses_count['AirMarksMissesCount']:
                if re.search('AirMarkMiss', group[0]):
                    for c in group[1:]:
                        air_marks.update(c)
                    container.append(air_marks)
                    marks_misses_count += 1
                    if marks_misses_count == misses_count['AirMarksMissesCount']:
                        break
            self.frame = self.frame[1:]
        return container

    @mapper
    def forbidden_sectors(self) -> list:
        container = []
        forbidden_sector = {'RadiationForbiddenSectorsCount': 0}
        rad_forbidden_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'\bRadiationForbiddenSectors\b', group[0]):
                for c in group[1:]:
                    forbidden_sector.update(c)
                self.frame = self.frame[index:]
            elif rad_forbidden_count < forbidden_sector['RadiationForbiddenSectorsCount']:
                if re.search(r'RadiationForbiddenSector', group[0]):
                    for c in group:
                        forbidden_sector.update(c)
                    container.append(forbidden_sector)
                    rad_forbidden_count += 1
                    self.frame = self.frame[index + 1:]
                    if rad_forbidden_count == forbidden_sector['RadiationForbiddenSectorsCount']:
                        self.frame = self.frame[1:]
                        break
            self.frame = self.frame[1:]
        return container
