import logging.config
import time
from pathlib import Path

from data_base_methods import DataBase
from read_blocks_from_telemetry import DataBlocksReader
from read_session_structure import read_session_structure
from read_session_telemetry import TelemetryFrameIterator

logging.config.fileConfig('../logging.conf')
console_log = logging.getLogger('simpleExample')
air_tracks_log = logging.getLogger('AirTracks_ForbSectors')
data_folder = Path(r'../data/session_01/')
planner = data_folder / r'Planner'
planner_rsf = data_folder / r'Planner.rsf'
frame_number = 2840

if __name__ == "__main__":
    structure = read_session_structure(planner)
    telemetry = TelemetryFrameIterator(planner_rsf, structure, frame_number)
    db = DataBase()
    start_parsing_time = time.time()
    candidate_history_pk_if_state_4 = 0
    air_track_hist_pk_if_state_4 = []
    for frame in telemetry:
        start_frame_time = time.time()
        frame_reader = DataBlocksReader(frame)
        forbidden_sectors_count = 1
        primary_marks_count = 1
        candidates_count = 1
        air_track_count = 1
        # ---------------------------------------------ЗАПОЛНЯЕМ "BeamTasks"------------------------------------------ #
        for beam_task in frame_reader.beam_tasks():
            bt_pk = db.get_pk_beam_tasks({'taskId': beam_task['taskId'],
                                          'antennaId': beam_task['antennaId'],
                                          'taskType': beam_task['taskType']})
            if bt_pk is None:
                db.insert_beam_tasks(beam_task)
            else:
                console_log.debug(f'BeamTask : already exists')
        # ---------------------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"--------------------------------------- #
        for prim_mark in frame_reader.primary_marks():
            console_log.info(f'\t\t\t\t\tPrimaryMark_{primary_marks_count}')
            console_log.info(f'PrimaryMark type = {prim_mark["markType"]}')
            bt_pk = db.get_pk_beam_tasks({'taskId': prim_mark['taskId'],
                                          'antennaId': prim_mark['antennaId'],
                                          'taskType': prim_mark['taskType']})
            if bt_pk:
                prim_mark.update({'BeamTask': bt_pk})
                pm_pk = db.get_pk_primary_marks({'BeamTask': prim_mark['BeamTask']})
                if pm_pk is None:
                    db.insert_prim_marks(prim_mark)
                else:
                    console_log.debug(f'PrimaryMark : already exists')
            primary_marks_count += 1
        # --------------------------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"-------------------------- #
        for candidate in frame_reader.candidates():
            console_log.info(f'\t\t\t\t\tCandidate_{candidates_count}')
            console_log.info(f'Candidate state = {candidate["state"]}')
            # -----------------------------------ЗАПОЛНЯЕМ "Candidates"-------------------------------- #
            cand_pk = db.get_pk_candidates(candidate['id'])
            if cand_pk is None:
                db.insert_candidates(candidate)
                cand_pk = db.get_pk_candidates(candidate['id'])
            candidate.update({'Candidate': cand_pk})
            # -----------------------------------ЗАПОЛНЯЕМ "CandidatesHistory"------------------------- #
            if candidate['state'] == 1:
                bt_pk = db.get_pk_beam_tasks({'trackId': candidate['id'], 'taskId': candidate['taskId'],
                                              'antennaId': candidate['antennaId'], 'taskType': 1})
            if candidate['state'] == 2:
                bt_pk = db.get_pk_beam_tasks({'trackId': candidate['id'], 'taskId': candidate['taskId'],
                                              'antennaId': candidate['antennaId'], 'taskType': 2})
            if bt_pk:
                candidate.update({'BeamTask': bt_pk})
                if candidate['state'] == 1 or candidate['state'] == 2:
                    pm_pk = db.get_pk_primary_marks({'BeamTask': candidate['BeamTask'],
                                                     'primaryMarkId': candidate['primaryMarkId']})
                    if pm_pk:
                        candidate.update({'PrimaryMark': pm_pk})
                        candidate_history_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                                     'PrimaryMark': candidate['PrimaryMark']})
                        if candidate_history_pk is None:
                            db.insert_cand_histories(candidate)
                            candidate_history_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                                         'PrimaryMark': candidate['PrimaryMark']})
                        # else:
                        #     console_log.debug(f'CandidateHistory : already exists')
                        # ------------------------ЗАПОЛНЯЕМ "AirTracksHistory"----------------------------- #
            if candidate['state'] == 4:
                console_log.debug(f'Need to get AirMarksUpdateRequests')
                for air_marks_upd_req in frame_reader.air_marks_update_requests():
                    if air_marks_upd_req['markId'] != candidate['id']:
                        console_log.warning(f'air_marks_upd_req["markId"] : {air_marks_upd_req["markId"]}'
                                            f' != candidate["id"] : {candidate["id"]}')
                    cand_pk = db.get_pk_candidates(air_marks_upd_req['markId'])
                    if cand_pk is None:
                        db.insert_candidates(candidate)
                        cand_pk = db.get_pk_candidates(air_marks_upd_req['markId'])
                    candidate.update({'Candidate': cand_pk})
                    bt_pk = db.get_pk_beam_tasks({'trackId': candidate['id'], 'taskId': candidate['taskId'],
                                                  'antennaId': air_marks_upd_req['antennaId'], 'taskType': 2})
                    if bt_pk:
                        candidate.update({'BeamTask': bt_pk})
                    candidate.update({'PrimaryMark': db.get_pk_primary_marks(
                        {'BeamTask': candidate['BeamTask'],
                         'primaryMarkId': candidate['primaryMarkId']})})
                    air_track_pk = db.get_pk_air_tracks(air_marks_upd_req['markId'])
                    if air_track_pk is None:
                        db.insert_air_tracks({'id': candidate['id']})
                        db.insert_air_tracks({'id': air_marks_upd_req['markId']})
                        air_track_pk = db.get_pk_air_tracks(air_marks_upd_req['markId'])
                    candidate.update({'AirTrack': air_track_pk})
                    candidate_history_pk_if_state_4 = db.get_pk_cand_hists(
                        {'BeamTask': candidate['BeamTask'],
                         'PrimaryMark': candidate['PrimaryMark'],
                         'Candidate': candidate['Candidate'],
                         'state': candidate['state']
                         })
                    if candidate_history_pk_if_state_4 is None:
                        db.insert_cand_histories(candidate)
                        candidate_history_pk_if_state_4 = db.get_pk_cand_hists(
                            {'BeamTask': candidate['BeamTask'],
                             'PrimaryMark': candidate['PrimaryMark'],
                             'Candidate': candidate['Candidate'],
                             'state': 4
                             })
                    candidate.update({'CandidatesHistory': candidate_history_pk})
                    air_track_hist_pk = db.get_pk_tracks_hists(
                        {'CandidatesHistory': candidate['CandidatesHistory'],
                         'PrimaryMark': candidate['PrimaryMark'],
                         'AirTrack': candidate['AirTrack'],
                         'antennaId': candidate['antennaId']
                         })
                    if air_track_hist_pk is None:
                        db.insert_air_tracks_histories(candidate)
                        air_track_hist_pk = db.get_pk_tracks_hists(
                            {'CandidatesHistory': candidate['CandidatesHistory'],
                             'PrimaryMark': candidate['PrimaryMark'],
                             'AirTrack': candidate['AirTrack'],
                             'antennaId': candidate['antennaId']
                             })
                    air_track_hist_pk_if_state_4.append(air_track_hist_pk)
            candidates_count += 1
        # ---------------------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"--------------------------- #
        for air_track in frame_reader.air_tracks():
            air_tracks_log.info(
                f'------------------------- FRAME {(telemetry.frame_index / 100)} -------------------------')
            console_log.info(f'\t\t\t\t\tAirTrack_{air_track_count}')
            console_log.info(f'AirTrack type = {air_track["type"]}')
            # --------------------------------------ЗАПОЛНЯЕМ "AirTracks"------------------------------ #
            air_track_pk = db.get_pk_air_tracks(air_track['id'])
            if air_track_pk is None:
                db.insert_air_tracks(air_track)
                air_track_pk = db.get_pk_air_tracks(air_track['id'])
            air_track.update({'AirTrack': air_track_pk})
            # ----------------------------------UPDATE "AirTracksHistory"------------------------------ #
            cand_pk_air = db.get_pk_candidates(air_track['id'])
            air_track_hist_pk = air_track_hist_pk_if_state_4[-1]
            if len(air_track_hist_pk_if_state_4) != 1:
                air_track_hist_pk_if_state_4.remove(air_track_hist_pk)
            console_log.debug(f'PK from AirTracksHistory received successfully : {air_track_hist_pk}')
            air_track.update({'AirTracksHistory': air_track_hist_pk})
            air_track.update(db.read_specific_field('AirTracksHistory', 'CandidatesHistory',
                                                    {'AirTracksHistory': air_track['AirTracksHistory']}))
            air_track.update(db.read_specific_field('CandidatesHistory', 'BeamTask',
                                                    {'CandidatesHistory': air_track['CandidatesHistory']}))
            air_track.update(db.read_specific_field('CandidatesHistory', 'PrimaryMark',
                                                    {'CandidatesHistory': air_track['CandidatesHistory']}))
            air_track.update(db.read_specific_field('BeamTasks', 'pulsePeriod',
                                                    {'BeamTask': air_track['BeamTask']}))
            air_track.update(db.read_specific_field('PrimaryMarks', 'scanTime',
                                                    {'PrimaryMark': air_track['PrimaryMark']}))
            db.update_air_tracks_histories(air_track)
            air_track_count += 1
        # ---------------------------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"----------------------------------- #
        for forbidden_sector in frame_reader.forbidden_sectors():
            console_log.info(f'\t\t\tforbiddenSector_{forbidden_sectors_count}')
            fs_pk = db.get_pk_forb_sectors({'azimuthBeginNSSK': ['azimuth_b_nssk'],
                                            'azimuthEndNSSK': ['azimuth_e_nssk'],
                                            'elevationBeginNSSK': ['elevation_b_nssk'],
                                            'elevationEndNSSK': ['elevation_e_nssk']})
            if fs_pk is None:
                fields = ["azimuth_b_nssk", "azimuth_e_nssk", "elevation_b_nssk", "elevation_e_nssk"]
                dict_to_insert = {k: v for k, v in forbidden_sector.items() if k in fields}
                db.insert_to_table('ForbiddenSectors', dict_to_insert)
            else:
                console_log.debug(f'ForbiddenSector : already exists')
            forbidden_sectors_count += 1
        time_sec = "{:3.4f}".format(time.time() - start_frame_time)
        console_log.info(f"------------------------- {time_sec} seconds -------------------------\r\n\r\n")
    minutes = "{:3.2f}".format(float(time.time() - start_parsing_time) / 60)
    console_log.info(f"------------------------- {minutes} minutes -------------------------\r\n\r\n")
