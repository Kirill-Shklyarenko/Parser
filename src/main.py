import logging.config
import time
from pathlib import Path

from data_base_methods import DataBase
from read_blocks_from_telemetry import DataBlocksReader
from read_session_structure import read_session_structure
from read_session_telemetry import TelemetryFrameIterator

logging.config.fileConfig('..\\logging.conf')
log = logging.getLogger('simpleExample')

data_folder = Path(r'../data/session_01/')
planner = data_folder / r'Planner'
planner_rsf = data_folder / r'Planner.rsf'
logger = data_folder / r'logger.log'
dsn = 'dbname=Telemetry user=postgres password=123 host=localhost'
frame_number = 20265

if __name__ == "__main__":
    structure = read_session_structure(planner)
    telemetry = TelemetryFrameIterator(planner_rsf, structure, frame_number)
    db = DataBase(dsn)
    start_parsing_time = time.time()
    for frame in telemetry:
        start_frame_time = time.time()
        frame_reader = DataBlocksReader(frame)
        primary_marks_count = 1
        candidates_count = 1
        air_track_count = 1
        forbidden_sectors_count = 1
        # ---------------------------------------------ЗАПОЛНЯЕМ "BeamTasks"------------------------------------------ #
        for beam_task in frame_reader.beam_tasks():
            beam_task_pk = db.get_pk_beam_tasks({'taskId': beam_task['taskId'], 'antennaId': beam_task['antennaId']})
            if beam_task_pk is None:
                fields = ['taskId', 'isFake', 'trackId', 'taskType', 'viewDirectionId', 'antennaId', 'pulsePeriod',
                          'threshold', 'lowerVelocityTrim', 'upperVelocityTrim', 'lowerDistanceTrim',
                          'upperDistanceTrim', 'beamAzimuth', 'beamElevation']
                dict_to_insert = {k: v for k, v in beam_task.items() if k in fields}
                db.insert_to_table('BeamTasks', dict_to_insert)
            else:
                log.debug(f'BeamTask : already exists')
        # ---------------------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"--------------------------------------- #
        for prim_mark in frame_reader.primary_marks():
            log.info(f'\t\t\t\t\tPrimaryMark_{primary_marks_count}')
            log.info(f'PrimaryMark type = {prim_mark["markType"]}')
            beam_task_pk = db.get_pk_beam_tasks({'taskId': prim_mark['taskId'], 'antennaId': prim_mark['antennaId'],
                                                 'taskType': prim_mark['taskType']})
            if beam_task_pk:
                prim_mark.update({'BeamTask': beam_task_pk})
                primary_mark_pk = db.get_pk_primary_marks({'BeamTask': prim_mark['BeamTask']})
                if primary_mark_pk is None:
                    fields = ["BeamTask", "primaryMarkId", "scanTime", "antennaId", "beamAzimuth", "beamElevation",
                              "azimuth", "elevation", "markType", "distance", "dopplerSpeed", "signalLevel",
                              "reflectedEnergy"]
                    dict_to_insert = {k: v for k, v in prim_mark.items() if k in fields}
                    db.insert_to_table('PrimaryMarks', dict_to_insert)
                else:
                    log.debug(f'PrimaryMark : already exists')
            primary_marks_count += 1
        # --------------------------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"-------------------------- #
        for candidate in frame_reader.candidates():
            log.info(f'\t\t\t\t\tCandidate_{candidates_count}')
            log.info(f'Candidate state = {candidate["state"]}')
            # -----------------------------------ЗАПОЛНЯЕМ "Candidates"-------------------------------- #
            candidates_pk = db.get_pk_candidates(candidate['id'])
            if candidates_pk is None:
                fields = ['id']
                dict_to_insert = {k: v for k, v in candidate.items() if k in fields}
                db.insert_to_table('Candidates', dict_to_insert)
            else:
                log.debug(f'Candidate : already exists')
            candidate.update({'Candidates': candidates_pk})
            # -----------------------------------ЗАПОЛНЯЕМ "CandidatesHistory"------------------------- #
            if candidate['state'] == 1:
                beam_task_pk_cand = db.get_pk_beam_tasks({'trackId': candidate['id'], 'taskId': candidate['taskId'],
                                                          'antennaId': candidate['antennaId'], 'taskType': 1})
            else:
                beam_task_pk_cand = db.get_pk_beam_tasks({'trackId': candidate['id'], 'taskId': candidate['taskId'],
                                                          'antennaId': candidate['antennaId'], 'taskType': 2})
                if beam_task_pk_cand:
                    candidate.update({'BeamTask': beam_task_pk_cand})

                if candidate['state'] != 4:
                    pm_pk_cand = db.get_pk_primary_marks({'BeamTask': candidate['BeamTask'],
                                                          'primaryMarkId': candidate['primaryMarkId']})
                    if pm_pk_cand:
                        candidate.update({'PrimaryMark': pm_pk_cand})
                        candidate_history_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                                     'PrimaryMark': candidate['PrimaryMark']})
                        if candidate_history_pk is None:
                            fields = ["BeamTask", "PrimaryMark", "Candidate", "azimuth", "elevation", "state",
                                      "distanceZoneWidth", "velocityZoneWidth", "numDistanceZone", "numVelocityZone",
                                      "antennaId", "timeUpdated"]
                            dict_to_insert = {k: v for k, v in candidate.items() if k in fields}
                            db.insert_to_table('CandidatesHistory', dict_to_insert)
                        else:
                            log.debug(f'CandidateHistory : already exists')
                    # ------------------------ЗАПОЛНЯЕМ "AirTracksHistory"----------------------------- #
            if candidate['state'] == 4:
                log.warning(f'Need to get AirMarksUpdateRequests')
                for air_marks_upd_req in frame_reader.air_marks_update_requests():

                    if air_marks_upd_req['markId'] != candidate['id']:
                        log.warning(f'air_marks_upd_req["markId"] : {air_marks_upd_req["markId"]}'
                                    f' != candidate["id"] : {candidate["id"]}')

                    candidate.update({'PrimaryMark': db.get_pk_primary_marks(
                        {'BeamTask': candidate['BeamTask'],
                         'primaryMarkId': candidate['primaryMarkId']})})

                    air_track_pk = db.get_pk_air_tracks(air_marks_upd_req['markId'])
                    if air_track_pk is None:
                        db.insert_to_table('AirTracks', {'id': air_marks_upd_req['markId']})
                        air_track_pk = db.get_pk_air_tracks(air_marks_upd_req['markId'])
                    candidate.update({'AirTrack': air_track_pk})

                    candidate.update({'Candidate': db.get_pk_candidates(air_marks_upd_req['markId'])})

                    candidate_history_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                                 'PrimaryMark': candidate['PrimaryMark'],
                                                                 'Candidate': candidate['Candidate']})
                    if candidate_history_pk is None:
                        fields = ["BeamTask", "PrimaryMark", "Candidate", "azimuth", "elevation", "distanceZoneWidth",
                                  "velocityZoneWidth", "numDistanceZone", "numVelocityZone", "state",
                                  "antennaId", "timeUpdated"]
                        dict_to_insert = {k: v for k, v in candidate.items() if k in fields}
                        db.insert_to_table('CandidatesHistory', dict_to_insert)
                        candidate_history_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                                     'PrimaryMark': candidate['PrimaryMark'],
                                                                     'Candidate': candidate['Candidate']})

                    candidate.update({'CandidatesHistory': candidate_history_pk})

                    air_track_hist_pk = db.get_pk_tracks_hists({'CandidatesHistory': candidate['CandidatesHistory'],
                                                                'PrimaryMark': candidate['PrimaryMark'],
                                                                'AirTrack': candidate['AirTrack']})
                    if air_track_hist_pk is None:
                        db.insert_to_table('AirTracksHistory', {'CandidatesHistory': candidate['CandidatesHistory'],
                                                                'PrimaryMark': candidate['PrimaryMark'],
                                                                'AirTrack': candidate['AirTrack']})
                    else:
                        log.debug(f'AirTracksHistory : already exists')
            candidates_count += 1
        # ---------------------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"--------------------------- #
        for air_track in frame_reader.air_tracks():
            log.info(f'\t\t\t\t\tAirTrack_{air_track_count}')
            log.info(f'AirTrack type = {air_track["type"]}')
            # --------------------------------------ЗАПОЛНЯЕМ "AirTracks"------------------------------ #
            air_track_pk = db.get_pk_air_tracks(air_track['id'])

            if air_track_pk is None:
                fields = ['id']
                dict_to_insert = {k: v for k, v in air_track.items() if k in fields}
                db.insert_to_table('AirTracks', dict_to_insert)
                air_track_pk = db.get_pk_air_tracks(air_track['id'])

            air_track.update({'AirTrack': air_track_pk})
            # ----------------------------------UPDATE "AirTracksHistory"------------------------------ #
            candidates_pk_air = db.get_pk_candidates(air_track['id'])
            cand_history_pk = db.get_pk_cand_hists({'Candidate': candidates_pk_air, 'state': 4})
            air_track.update({'CandidatesHistory': cand_history_pk})
            air_track.update(db.read_specific_field('CandidatesHistory', 'BeamTask',
                                                    {'CandidatesHistory': air_track['CandidatesHistory']}))
            air_track.update(db.read_specific_field('CandidatesHistory', 'PrimaryMark',
                                                    {'CandidatesHistory': air_track['CandidatesHistory']}))
            if air_track['PrimaryMark']:
                air_track.update(db.read_specific_field('BeamTasks', 'pulsePeriod',
                                                        {'BeamTask': air_track['BeamTask']}))
                air_track.update(db.read_specific_field('PrimaryMarks', 'scanTime',
                                                        {'PrimaryMark': air_track['PrimaryMark']}))
                air_marks_misses = frame_reader.air_marks_misses()
                if air_marks_misses:
                    air_track.update({'missesCount': air_marks_misses})
                fields = ["PrimaryMark", "CandidatesHistory", "AirTrack", "type", "priority",
                          "antennaId", "azimuth", "elevation", "distance", "radialVelocity",
                          "pulsePeriod", "missesCount", "possiblePeriods", "timeUpdated",
                          "scanPeriod", "sigmaAzimuth", "sigmaElevation", "sigmaDistance",
                          "sigmaRadialVelocity", "minDistance", "maxDistance", "minRadialVelocity",
                          "maxRadialVelocity", "scanTime"]
                air_track_m = {k: v for k, v in air_track.items() if k in fields}
                air_track_hist_pk = db.get_pk_tracks_hists({'CandidatesHistory': air_track_m['CandidatesHistory'],
                                                            'PrimaryMark': air_track_m['PrimaryMark']})
                air_track_m.update({'AirTracksHistory': air_track_hist_pk})
                db.update_tables('AirTracksHistory', air_track_m,
                                 {'AirTracksHistory': air_track_m['AirTracksHistory'],
                                  'CandidatesHistory': air_track_m['CandidatesHistory'],
                                  'PrimaryMark': air_track_m['PrimaryMark']})
            air_track_count += 1
            # ---------------------------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"--------------------------- #
            for forbidden_sector in frame_reader.forbidden_sectors():
                log.info(f'\t\t\tforbiddenSector_{forbidden_sectors_count}')
                fs_pk = db.get_pk_forb_sectors(forbidden_sector['azimuth_b_nssk'],
                                               forbidden_sector['azimuth_e_nssk'],
                                               forbidden_sector['elevation_b_nssk'],
                                               forbidden_sector['elevation_e_nssk'])
                if fs_pk is None:
                    fields = ["azimuth_b_nssk", "azimuth_e_nssk", "elevation_b_nssk", "elevation_e_nssk"]
                    dict_to_insert = {k: v for k, v in forbidden_sector.items() if k in fields}
                    db.insert_to_table('ForbiddenSectors', dict_to_insert)
                else:
                    log.debug(f'ForbiddenSector : already exists')
                forbidden_sectors_count += 1
            # - FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN --  #
            time_sec = "{:3.4f}".format(time.time() - start_frame_time)
            log.info(f"------------------------- {time_sec} seconds -------------------------\r\n\r\n")

    minutes = "{:3.2f}".format(float(time.time() - start_parsing_time) / 60)
    log.info(f"------------------------- {minutes} minutes -------------------------\r\n\r\n")
