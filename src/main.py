import logging.config
import time
from pathlib import Path

from data_base_methods import DataBase
from read_blocks_from_telemetry import DataBlocksReader
from read_session_structure import read_session_structure
from read_session_telemetry import TelemetryFrameIterator

logging.config.fileConfig('../logging.conf')
console_log = logging.getLogger('simpleExample')
tracks_log = logging.getLogger('AirTracks_ForbSectors')
data_folder = Path(r'../data/session_01/')
planner = data_folder / r'Planner'
planner_rsf = data_folder / r'Planner.rsf'
frame_number = 0

if __name__ == "__main__":
    structure = read_session_structure(planner)
    telemetry = TelemetryFrameIterator(planner_rsf, structure, frame_number)
    db = DataBase()
    start_parsing_time = time.time()
    # -------# # -------# # -------# # -------# # -------# # -------#
    beam_task_count = 1
    prim_mark_count = 1
    candidate_count = 1
    air_tracks_count = 1
    forbidden_sector_count = 1
    cand_hist_pk_if_state_4 = []
    air_track_hist_pk_if_state_4 = []
    last_cand_hist_pk_if_state_4 = None
    last_air_track_hist_pk_if_state_4 = None
    # -------# # -------# # -------# # -------# # -------# # -------#
    for frame in telemetry:
        if cand_hist_pk_if_state_4:
            last_cand_hist_pk_if_state_4 = cand_hist_pk_if_state_4[-1]
        if air_track_hist_pk_if_state_4:
            last_air_track_hist_pk_if_state_4 = air_track_hist_pk_if_state_4[-1]
        start_frame_time = time.time()
        frame_reader = DataBlocksReader(frame)
        # ---------------------------------------------ЗАПОЛНЯЕМ "BeamTasks"------------------------------------------ #
        for beam_task in frame_reader.beam_tasks():
            console_log.info(f'\t\t\t\t\t\t\tBeamTask_{beam_task_count}')
            beam_task_count += 1
            bt_pk = db.get_pk_beam_tasks({'taskId': beam_task['taskId'],
                                          'antennaId': beam_task['antennaId'],
                                          'taskType': beam_task['taskType']})
            if bt_pk is None:
                db.insert_beam_tasks(beam_task)
            else:
                console_log.debug(f'BeamTask : already exists')
        # ---------------------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"--------------------------------------- #
        for prim_mark in frame_reader.primary_marks():
            console_log.info(f'\t\t\t\t\t\t\tPrimaryMark_{prim_mark_count}')
            prim_mark_count += 1
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
        # --------------------------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"-------------------------- #
        for candidate in frame_reader.candidates():
            console_log.info(f'\t\t\t\t\t\t\tCandidate_{candidate_count}')
            candidate_count += 1
            console_log.info(f'Candidate state = {candidate["state"]}')
            # -----------------------------------ЗАПОЛНЯЕМ "Candidates"-------------------------------- #
            cand_pk_with_mark_id = db.get_pk_candidates(candidate['id'])
            if cand_pk_with_mark_id is None:
                db.insert_candidates(candidate)
                cand_pk_with_mark_id = db.get_pk_candidates(candidate['id'])
            candidate.update({'Candidate': cand_pk_with_mark_id})
            # -----------------------------------ЗАПОЛНЯЕМ "CandidatesHistory"------------------------- #
            if candidate['state'] == 1:
                bt_pk = db.get_pk_beam_tasks({'trackId': candidate['id'], 'taskId': candidate['taskId'],
                                              'antennaId': candidate['antennaId'], 'taskType': 1})
            else:
                bt_pk = db.get_pk_beam_tasks({'trackId': candidate['id'], 'taskId': candidate['taskId'],
                                              'antennaId': candidate['antennaId'], 'taskType': 2})
            if bt_pk:
                candidate.update({'BeamTask': bt_pk})
                pm_pk = db.get_pk_primary_marks({'BeamTask': candidate['BeamTask'],
                                                 'primaryMarkId': candidate['primaryMarkId']})
                if pm_pk:
                    candidate.update({'PrimaryMark': pm_pk})
                    if candidate['state'] != 4:
                        cand_hist_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                             'PrimaryMark': candidate['PrimaryMark'],
                                                             'Candidate': candidate['Candidate'],
                                                             'state': candidate['state'],
                                                             })
                        if cand_hist_pk is None:
                            db.insert_cand_histories(candidate)
            # ------------------------------------ЗАПОЛНЯЕМ "AirTracksHistory"------------------------- #
            if candidate['state'] == 4:
                console_log.debug(f'Need to check with air_marks_update_requests[id]')
                for air_marks_upd_req in frame_reader.air_marks_update_requests():
                    cand_pk_with_mark_id = db.get_pk_candidates(air_marks_upd_req['markId'])
                    if cand_pk_with_mark_id is None:
                        db.insert_candidates(candidate)
                        cand_pk_with_mark_id = db.get_pk_candidates(air_marks_upd_req['markId'])
                    # ----------------- ## ----------------- ## ----------------- #
                    candidate.update({'Candidate': cand_pk_with_mark_id})
                    console_log.debug(f'Need to insert in AirTracks if not exist')
                    air_track_pk_with_mark_id = db.get_pk_air_tracks(air_marks_upd_req['markId'])
                    if air_track_pk_with_mark_id is None:
                        db.insert_air_tracks({'id': air_marks_upd_req['markId']})
                        air_track_pk_with_mark_id = db.get_pk_air_tracks(air_marks_upd_req['markId'])
                    # ----------------- ## ----------------- ## ----------------- #
                    candidate.update({'AirTrack': air_track_pk_with_mark_id})
                    cand_hist_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                         'PrimaryMark': candidate['PrimaryMark'],
                                                         'Candidate': candidate['Candidate'],
                                                         'state': candidate['state'],
                                                         })
                    if cand_hist_pk is None:
                        db.insert_cand_histories(candidate)
                        cand_hist_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                             'PrimaryMark': candidate['PrimaryMark'],
                                                             'Candidate': candidate['Candidate'],
                                                             'state': candidate['state'],
                                                             })
                    # -------# # -------# # -------# # -------# # -------# # -------#
                    if last_cand_hist_pk_if_state_4 is None:
                        cand_hist_pk_if_state_4.append(cand_hist_pk)
                        last_cand_hist_pk_if_state_4 = cand_hist_pk
                    if last_cand_hist_pk_if_state_4 != cand_hist_pk:
                        if cand_hist_pk not in cand_hist_pk_if_state_4:
                            cand_hist_pk_if_state_4.append(cand_hist_pk)
                            last_cand_hist_pk_if_state_4 = cand_hist_pk
                    # ----------------- ## ----------------- ## ----------------- #
                    candidate.update({'CandidatesHistory': last_cand_hist_pk_if_state_4})
                    a_tr_hist_pk = db.get_pk_tracks_hists({
                        'AirTrack': candidate['AirTrack'],
                        'PrimaryMark': candidate['PrimaryMark'],
                        'antennaId': candidate['antennaId'],
                        'CandidatesHistory': candidate['CandidatesHistory'],
                    })
                    if a_tr_hist_pk is None:
                        db.insert_air_tracks_histories(candidate)
                        a_tr_hist_pk = db.get_pk_tracks_hists({'AirTrack': candidate['AirTrack'],
                                                               'PrimaryMark': candidate['PrimaryMark'],
                                                               'antennaId': candidate['antennaId'],
                                                               'CandidatesHistory': candidate['CandidatesHistory'],
                                                               })
                    # -------# # -------# # -------# # -------# # -------# # -------#
                    if last_air_track_hist_pk_if_state_4 is None:
                        air_track_hist_pk_if_state_4.append(a_tr_hist_pk)
                        last_air_track_hist_pk_if_state_4 = a_tr_hist_pk
                    if last_air_track_hist_pk_if_state_4 != a_tr_hist_pk:
                        if a_tr_hist_pk not in air_track_hist_pk_if_state_4:
                            air_track_hist_pk_if_state_4.append(a_tr_hist_pk)
                            last_air_track_hist_pk_if_state_4 = a_tr_hist_pk
                    # -------# # -------# # -------# # -------# # -------# # -------#
        # ---------------------------------------UPDATE "AirTracksHistory"-------------------------------------------- #
        for air_track in frame_reader.air_tracks():
            if air_track['possiblePeriods'][0] != 0 and air_track['possiblePeriods'][1] != 0 \
                    and air_track['possiblePeriods'][2] != 0 and air_track['possiblePeriods'][3] != 0 \
                    and air_track['possiblePeriods'][4] != 0 and air_track['possiblePeriods'][5] != 0:
                console_log.warning(f'REAL AIR TRACK DETECTED')
            tracks_log.info(f' FRAME {(telemetry.frame_id / 100):{3}.{2}}')
            console_log.info(f'\t\t\t\t\t\t\tAirTrack_{air_tracks_count}')
            air_tracks_count += 1
            # ----------------------------------UPDATE "AirTracksHistory"-------------------------- #
            air_track_pk_with_mark_id = db.get_pk_air_tracks(air_track['id'])
            if air_track_pk_with_mark_id:
                # ----------------- ## ----------------- ## ----------------- #
                air_track.update({'AirTrack': air_track_pk_with_mark_id})
                if last_air_track_hist_pk_if_state_4:
                    console_log.debug(f'PK from AirTracksHistory received successfully :'
                                      f' {last_air_track_hist_pk_if_state_4}')
                    air_track.update({'AirTracksHistory': last_air_track_hist_pk_if_state_4})
                    air_track.update(db.read_specific_field('AirTracksHistory', 'CandidatesHistory',
                                                            {'AirTracksHistory': air_track['AirTracksHistory']}))
                    # ----------------- ## ----------------- ## ----------------- #
                    air_track.update(db.read_specific_field('CandidatesHistory', 'BeamTask',
                                                            {'CandidatesHistory': air_track['CandidatesHistory']}))
                    air_track.update(db.read_specific_field('CandidatesHistory', 'PrimaryMark',
                                                            {'CandidatesHistory': air_track['CandidatesHistory']}))
                    air_track.update(db.read_specific_field('BeamTasks', 'pulsePeriod',
                                                            {'BeamTask': air_track['BeamTask']}))
                    air_track.update(db.read_specific_field('PrimaryMarks', 'scanTime',
                                                            {'PrimaryMark': air_track['PrimaryMark']}))
                    # ----------------- ## ----------------- ## ----------------- #
                    db.update_air_tracks_histories(air_track)
        # ---------------------------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"----------------------------------- #
        for forbidden_sector in frame_reader.forbidden_sectors():
            console_log.info(f'\t\t\t\t\tForbiddenSector{forbidden_sector_count}')
            forbidden_sector += 1
            fs_pk = db.get_pk_forb_sectors({'azimuthBeginNSSK': ['azimuth_b_nssk'],
                                            'azimuthEndNSSK': ['azimuth_e_nssk'],
                                            'elevationBeginNSSK': ['elevation_b_nssk'],
                                            'elevationEndNSSK': ['elevation_e_nssk']})
            if fs_pk is None:
                fields = ["azimuth_b_nssk", "azimuth_e_nssk", "elevation_b_nssk", "elevation_e_nssk"]
                dict_to_insert = {k: v for k, v in forbidden_sector.items() if k in fields}
                # ------------------------# ------------------------# ------------------------
                db.insert_to_table('ForbiddenSectors', dict_to_insert)
            else:
                console_log.debug(f'ForbiddenSector : already exists')
        console_log.info(f'{(25 * "-")} {(time.time() - start_frame_time):{3}.{4}} Secs {(25 * "-")}\r\n')
    console_log.info(f'{(25 * "-")} {(float(time.time() - start_parsing_time) / 60):{3}.{2}} Mins {(25 * "-")}\r\n')
