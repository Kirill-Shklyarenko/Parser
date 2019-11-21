import copy
import io
import logging as log
import os
import re
from struct import *

from decorators import mapper


class TelemetryReader:
    def __init__(self, file_name: str, data_struct: object):
        self.file_name = file_name
        self.data_struct = data_struct.__dict__['data_struct']
        self.frame_size = data_struct.__dict__['frame_size']
        self.frame_number = 0

        self.buff_size = (self.frame_size * 2) - 6  # need 16072 bytes
        self.frames_range = self.frame_counter()
        self.serialize_string = self.create_serialize_string()
        self.file_obj = self.open()

    def open(self):
        file = io.open(self.file_name, 'rb', buffering=0)
        return file

    def frame_counter(self) -> int:
        file_size = os.path.getsize(self.file_name) - 14  # Размер файла в байтах # отсекаем 14 байт заголовка
        frames_count = 0
        try:
            frames_count = file_size / (self.frame_size * 2)
        except ZeroDivisionError as e:
            log.exception(f'{e} , {frames_count}')
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
                    elif 'RR' in c['type']:  # char
                        serialize_string += 'c'
                    elif 'FF' in c['type']:
                        serialize_string += 'f'  # float_4
        return serialize_string

    def read_frame(self) -> list:
        frame_values = None
        frame_rate = self.frame_number * (self.frame_size * 2)
        buffer = self.file_obj.read(self.buff_size + frame_rate)
        buffer = buffer[frame_rate:]
        buffer = buffer[:self.buff_size]
        buffer = buffer[14:]
        try:
            frame_values = list(unpack(self.serialize_string, buffer))
        except Exception as e:
            log.exception(f'Exception: {e}')
        finally:
            log.info(f'----------------------- FRAME {self.frame_number} ------------------')
            frame = copy.deepcopy(self.data_struct)
            group_names = []
            for number, line in enumerate(frame):
                group_names.append(line[0])
                for c in line:
                    if type(c) is dict:
                        key = c.get('name')
                        c.clear()
                        value = frame_values[0]
                        frame_values.pop(0)
                        c.update({key: value})
            # formatted = pformat(frame, width=105, compact=True)
            # for line in formatted.splitlines():
            #     log.info(line.rstrip())
        return frame[2:]

    def __iter__(self):
        return self

    def __next__(self):
        result = None
        try:
            if self.frame_number < self.frames_range:
                result = self.read_frame()
            else:
                self.file_obj.close()
        except IndexError:
            raise StopIteration
        self.frame_number += 1
        return result


# ----------------------- #  ----------------------- # ----------------------- # ---------------------- #
# ----------------------- #  ----------------------- # ----------------------- # ---------------------- #
# ----------------------- #  ----------------------- # ----------------------- # ---------------------- #
class FrameHandler:
    def __init__(self, frame):
        self.frame = frame

    @mapper
    def beam_tasks(self):
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
    def primary_marks(self):
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
    def candidates(self):
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
    def air_tracks(self):
        container = []
        track = {}
        tracks_q = {'tracksQueuesSize': 0}
        tracks_count = 0
        for index, group in enumerate(self.frame):
            if type(group[0]) is not str:
                breakpoint()
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

    @mapper
    def forbidden_sectors(self):
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
