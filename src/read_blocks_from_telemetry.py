import logging.config
import re
import textwrap

from decorators import converter

air_tracks_log = logging.getLogger('AirTracks_ForbSectors')


class DataBlocksReader:
    __slots__ = 'frame'

    def __init__(self, frame):
        self.frame = frame

    @converter({'beamAzimuth': 'betaBSK', 'beamElevation': 'epsilonBSK'})  # {newField : oldField, newField : oldField}
    def beam_tasks(self) -> list:
        container = []
        task = {}
        beam_task = {}
        for index, group in enumerate(self.frame):
            if re.search(r'\bTask\b', group[0][0]):
                for c in group[1]:
                    task.update(c)
            elif re.search(r'beamTask', group[0][0]):
                beam_task.update(task)
                for c in group[1]:
                    beam_task.update(c)
                beam_task.update({k: bool(v) for k, v in beam_task.items() if k == 'isFake'})
                container.append(beam_task.copy())
            elif re.search('scanData', group[0][0]):
                break
        return container

    @converter({'primaryMarkId': 'id', 'markType': 'type', 'scanTime': 'processingTime'})
    def primary_marks(self) -> list:
        container = []
        primary_mark = {}
        scan_data = {'primaryMarksCount': 0}
        primary_marks_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'scanData', group[0][0]):
                for c in group[1]:
                    scan_data.update(c)
            elif primary_marks_count < scan_data['primaryMarksCount']:
                if re.search(r'primaryMark', group[0][0]):
                    for c in group[1]:
                        primary_mark.update(c)
                    primary_mark.update(scan_data)
                    container.append(primary_mark.copy())
                    primary_marks_count += 1
                    if primary_marks_count == scan_data['primaryMarksCount']:
                        break
        return container

    @converter({'timeUpdated': 'creationTimeSeconds'})
    def candidates(self) -> list:
        container = []
        track_candidate = {'state': 0}
        candidate_q = {'candidatesQueueSize': 0}
        candidates_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'TrackCandidates', group[0][0]):
                candidate_q = {}
                for c in group[1]:
                    candidate_q.update(c)
            elif candidates_count < candidate_q['candidatesQueueSize']:
                if re.search(r'\btrackCandidate\b', group[0][0]) or re.search('trackCandidate_', group[0][0]):
                    for c in group[1]:
                        track_candidate.update(c)
                elif track_candidate['antennaId'] != 0:
                    if track_candidate['state'] == 1:
                        if re.search(r'viewSpot', group[0][0]):
                            view_spot = {}
                            for c in group[1]:
                                view_spot.update(c)
                            track_candidate.update(view_spot)
                            container.append(track_candidate.copy())
                            candidates_count += 1
                            if candidates_count == candidate_q['candidatesQueueSize']:
                                break
                    elif track_candidate['state'] == 2:
                        if re.search(r'distanceResolutionSpot', group[0][0]):
                            distance_res_spot = {}
                            for c in group[1]:
                                distance_res_spot.update(c)
                            track_candidate.update(distance_res_spot)
                            track_candidate.update({'distanceZoneWidth': (track_candidate['resolvedDistance'] -
                                                                          track_candidate['distance']) /
                                                                         track_candidate[
                                                                             'distancePeriod']})
                            track_candidate.update({'numDistanceZone': round(track_candidate['resolvedDistance'] /
                                                                             track_candidate['distancePeriod'])})
                            container.append(track_candidate.copy())
                            candidates_count += 1
                            if candidates_count == candidate_q['candidatesQueueSize']:
                                break
                    elif track_candidate['state'] == 4:
                        if re.search(r'velocityResolutionSpot', group[0][0]):
                            velocity_res_spot = {}
                            for c in group[1]:
                                velocity_res_spot.update(c)
                            track_candidate.update(velocity_res_spot)
                            track_candidate.update({'distanceZoneWidth': (track_candidate['resolvedDistance'] -
                                                                          track_candidate['distance']) /
                                                                         track_candidate[
                                                                             'distancePeriod']})
                            track_candidate.update({'numDistanceZone': round(track_candidate['resolvedDistance'] /
                                                                             track_candidate['distancePeriod'])})
                            track_candidate.update({'velocityZoneWidth': (track_candidate['resolvedVelocity'] -
                                                                          track_candidate['velocity']) /
                                                                         track_candidate[
                                                                             'velocityPeriod']})
                            track_candidate.update({'numVelocityZone': round(track_candidate['resolvedVelocity'] /
                                                                             track_candidate['velocityPeriod'])})
                            container.append(track_candidate.copy())
                            candidates_count += 1
                            if candidates_count == candidate_q['candidatesQueueSize']:
                                break
                    else:
                        candidates_count += 1
                        if candidates_count == candidate_q['candidatesQueueSize']:
                            break
        container.reverse()
        return container

    @converter({'timeUpdated': 'nextUpdateTimeSeconds', 'scanPeriod': 'scanPeriodSeconds'})
    def air_tracks(self) -> list:
        container = []
        track = {}
        tracks_q = {'tracksQueuesSize': 0}
        tracks_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'\bTracks\b', group[0][0]):
                tracks_q = {}
                for c in group[1]:
                    tracks_q.update(c)
            elif tracks_count < tracks_q['tracksQueuesSize']:
                if re.search(r'\btrack\b', group[0][0]) or re.search('track_', group[0][0]):
                    for c in group[1]:
                        track.update(c)
                    if track['antennaId'] != 0:
                        track.update({'possiblePeriods': [track['possiblePeriod[0]'], track['possiblePeriod[1]'],
                                                          track['possiblePeriod[2]'], track['possiblePeriod[3]'],
                                                          track['possiblePeriod[4]'], track['possiblePeriod[5]'], ]})
                        # del [track['possiblePeriod[0]'], track['possiblePeriod[1]'],
                        #      track['possiblePeriod[2]'], track['possiblePeriod[3]'],
                        #      track['possiblePeriod[4]'], track['possiblePeriod[5]'], ]
                        if track['possiblePeriods'][0] != 0 and track['possiblePeriods'][1] != 0 \
                                and track['possiblePeriods'][2] != 0 and track['possiblePeriods'][3] != 0 \
                                and track['possiblePeriods'][4] != 0 and track['possiblePeriods'][5] != 0:
                            container.append(track.copy())
                        tracks_count += 1
                    if tracks_count == tracks_q['tracksQueuesSize']:
                        break
        if container:
            container.reverse()
            # air_tracks_log.info(textwrap.fill(f'\tAirTrack : {container}', 150, ))
        return container

    def air_marks_misses(self) -> list:
        container = []
        air_marks = {}
        misses_count = {'AirMarksMissesCount': 0}
        marks_misses_count = 0
        for group in self.frame:
            if re.search(r'AirMarksMissesCount', group[0][0]):
                for c in group[1]:
                    misses_count.update(c)
            elif marks_misses_count < misses_count['AirMarksMissesCount']:
                if re.search('AirMarkMiss', group[0][0]):
                    for c in group[1]:
                        air_marks.update(c)
                    if air_marks['markId'] != 0:
                        container.append(air_marks.copy())
                    marks_misses_count += 1
            elif re.search('TargetingUpdateRequests', group[0][0]):
                break
        if container:
            container.reverse()
            # air_tracks_log.info(textwrap.fill(f'\t\tAirMarkMiss : {container}', 150, ))
        return container

    def air_marks_update_requests(self):
        container = []
        air_marks_upd_req = {}
        misses_count = {'AirMarksUpdateRequestsCount': 0}
        air_marks_upd_count = 0
        for group in self.frame:
            if re.search(r'AirMarksUpdateRequests', group[0][0]):
                for c in group[1]:
                    misses_count.update(c)
            elif air_marks_upd_count < misses_count['AirMarksUpdateRequestsCount']:
                if re.search(r'\bAirMarkUpdateRequest\b', group[0][0]) or re.search('AirMarkUpdateRequest_',
                                                                                    group[0][0]):
                    for c in group[1]:
                        air_marks_upd_req.update(c)
                    if air_marks_upd_req['markId'] != 0 and air_marks_upd_req['antennaId'] != 0:
                        container.append(air_marks_upd_req.copy())
                    air_marks_upd_count += 1
                elif re.search('TargetingUpdateRequests', group[0][0]):
                    break
        if container:
            container.reverse()
            air_tracks_log.info(textwrap.fill(f'{(3 * "    ")}AirMarksUpdateRequests : {container}', 150, ))
        return container

    @converter({'azimuthBeginNSSK': 'minAzimuth', 'azimuthEndNSSK': 'maxAzimuth',
                'elevationBeginNSSK': 'minElevation', 'elevationEndNSSK': 'maxElevation'})
    def forbidden_sectors(self) -> list:
        container = []
        forbidden_sector = {'RadiationForbiddenSectorsCount': 0}
        rad_forbidden_count = 0
        for index, group in enumerate(self.frame):
            if re.search(r'\bRadiationForbiddenSectors\b', group[0][0]):
                for c in group[1]:
                    forbidden_sector.update(c)
            elif rad_forbidden_count < forbidden_sector['RadiationForbiddenSectorsCount']:
                if re.search(r'RadiationForbiddenSector', group[0][0]):
                    for c in group:
                        forbidden_sector.update(c)
                    container.append(forbidden_sector.copy())
                    rad_forbidden_count += 1
                    if rad_forbidden_count == forbidden_sector['RadiationForbiddenSectorsCount']:
                        break
        # if container:
        # air_tracks_log.info(textwrap.fill(f'\t\t\t\tRadiationForbiddenSector : {container}', 150, ))
        return container
