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

    cand_hist_pk_if_state_2 = []
    cand_hist_pk_if_state_4 = []
    air_track_hist_pk_if_state_4 = []

    last_cand_hist_pk_if_state_2 = None
    last_cand_hist_pk_if_state_4 = None
    last_air_track_hist_pk_if_state_4 = None

    for frame in telemetry:
        if cand_hist_pk_if_state_2:
            last_cand_hist_pk_if_state_2 = cand_hist_pk_if_state_2[-1]
        if cand_hist_pk_if_state_4:
            last_cand_hist_pk_if_state_4 = cand_hist_pk_if_state_4[-1]
        if air_track_hist_pk_if_state_4:
            last_air_track_hist_pk_if_state_4 = air_track_hist_pk_if_state_4[-1]

        start_frame_time = time.time()
        frame_reader = DataBlocksReader(frame)  # Session20
        # ---------------------------------------------ЗАПОЛНЯЕМ "BeamTasks"------------------------------------------ #
        for beam_task in frame_reader.beam_tasks():
            x = frame_reader.entity_count
            console_log.info(f'\t\t\t\t\tBeamTask_{x[0]}')
            del x[0]
            bt_pk = db.get_pk_beam_tasks({'taskId': beam_task['taskId'],
                                          'antennaId': beam_task['antennaId'],
                                          'taskType': beam_task['taskType']})
            if bt_pk is None:
                db.insert_beam_tasks(beam_task)
            else:
                console_log.debug(f'BeamTask : already exists')
        # ---------------------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"--------------------------------------- #
        for prim_mark in frame_reader.primary_marks():
            x = frame_reader.entity_count
            console_log.info(f'\t\t\t\t\tPrimaryMark_{x[0]}')
            del x[0]
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
            x = frame_reader.entity_count
            console_log.info(f'\t\t\t\t\tCandidate_{x[0]}')
            del x[0]
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
            else:
                bt_pk = db.get_pk_beam_tasks({'trackId': candidate['id'], 'taskId': candidate['taskId'],
                                              'antennaId': candidate['antennaId'], 'taskType': 2})
            if bt_pk:
                candidate.update({'BeamTask': bt_pk})
                pm_pk = db.get_pk_primary_marks({'BeamTask': candidate['BeamTask'],
                                                 'primaryMarkId': candidate['primaryMarkId']})
                if pm_pk:
                    candidate.update({'PrimaryMark': pm_pk})
                    candidate_history_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                                 'PrimaryMark': candidate['PrimaryMark'],
                                                                 'Candidate': candidate['Candidate'],
                                                                 'state': candidate['state'],
                                                                 })
                    if candidate_history_pk is None:
                        db.insert_cand_histories(candidate)
                        candidate_history_pk = db.get_pk_cand_hists({'BeamTask': candidate['BeamTask'],
                                                                     'PrimaryMark': candidate['PrimaryMark'],
                                                                     'Candidate': candidate['Candidate'],
                                                                     'state': candidate['state'],
                                                                     })
                    if candidate['state'] == 4:
                        if last_cand_hist_pk_if_state_4 is None:
                            cand_hist_pk_if_state_4.append(candidate_history_pk)
                            last_cand_hist_pk_if_state_4 = candidate_history_pk
                        if last_cand_hist_pk_if_state_4 != candidate_history_pk:
                            if candidate_history_pk not in last_cand_hist_pk_if_state_4:
                                cand_hist_pk_if_state_4.append(candidate_history_pk)
                                last_cand_hist_pk_if_state_4 = candidate_history_pk
            # ------------------------ЗАПОЛНЯЕМ "AirTracksHistory"------------------------------------- #
            if candidate['state'] == 4:
                console_log.debug(f'Need to check with air_marks_update_requests[id]')
                for air_marks_upd_req in frame_reader.air_marks_update_requests():
                    cand_pk = db.get_pk_candidates(air_marks_upd_req['markId'])
                    if cand_pk is None:
                        db.insert_candidates(candidate)
                        cand_pk = db.get_pk_candidates(air_marks_upd_req['markId'])
                    candidate.update({'Candidate': cand_pk})
                    air_track_pk_if_state_4 = db.get_pk_air_tracks(air_marks_upd_req['markId'])
                    if air_track_pk_if_state_4 is None:
                        db.insert_air_tracks({'id': air_marks_upd_req['markId']})
                        air_track_pk = db.get_pk_air_tracks(air_marks_upd_req['markId'])
                    candidate.update({'AirTrack': air_track_pk_if_state_4})
                    if bt_pk:
                        candidate.update({'BeamTask': bt_pk})
                        candidate.update({'CandidatesHistory': last_cand_hist_pk_if_state_4})
                        db.update_candidate_histories(candidate)  # DB UPDATE
                        a_tr_hist_pk = db.get_pk_tracks_hists({'CandidatesHistory': candidate['CandidatesHistory'],
                                                               'PrimaryMark': candidate['PrimaryMark'],
                                                               'AirTrack': candidate['AirTrack'],
                                                               'antennaId': candidate['antennaId']
                                                               })
                        if a_tr_hist_pk is None:
                            db.insert_air_tracks_histories(candidate)
                            a_tr_hist_pk = db.get_pk_tracks_hists({'CandidatesHistory': candidate['CandidatesHistory'],
                                                                   'PrimaryMark': candidate['PrimaryMark'],
                                                                   'AirTrack': candidate['AirTrack'],
                                                                   'antennaId': candidate['antennaId']
                                                                   })
                        # -------# # -------# # -------# # -------# # -------# # -------#
                        if air_track_hist_pk_if_state_4 is None:
                            air_track_hist_pk_if_state_4.append(a_tr_hist_pk)
                            last_air_track_hist_pk_if_state_4 = a_tr_hist_pk
                        if last_air_track_hist_pk_if_state_4 != a_tr_hist_pk:
                            if a_tr_hist_pk not in air_track_hist_pk_if_state_4:
                                air_track_hist_pk_if_state_4.append(a_tr_hist_pk)
                                last_air_track_hist_pk_if_state_4 = a_tr_hist_pk
        # ---------------------------------------UPDATE "AirTracksHistory"-------------------------------------------- #
        for air_track in frame_reader.air_tracks():
            poss_per = air_track['possiblePeriods']
            if poss_per[0] != 0 and poss_per[1] != 0 and poss_per[2] != 0 \
                    and poss_per[3] != 0 and poss_per[4] != 0 and poss_per[5] != 0:
                tracks_log.info(
                    f'------------------------- FRAME {(telemetry.frame_id / 100)} -------------------------')
                x = frame_reader.entity_count
                console_log.info(f'\t\t\t\t\tAirTrack_{x[0]}')
                del x[0]
                air_track_pk = db.get_pk_air_tracks(air_track['id'])
                if air_track_pk:
                    air_track.update({'AirTrack': air_track_pk})
                    # ----------------------------------UPDATE "AirTracksHistory"-------------------------- #
                    if len(air_track_hist_pk_if_state_4) == 1:
                        last_air_track_pk = air_track_hist_pk_if_state_4[0]
                    if last_cand_hist_pk_if_state_4:
                        console_log.debug(f'PK from CandidatesHistory '
                                          f'received successfully : {last_cand_hist_pk_if_state_4}')
                        air_track.update({'CandidatesHistory': last_cand_hist_pk_if_state_4})
                    # ------------------------# ------------------------# ------------------------
                    if last_air_track_pk:
                        console_log.debug(f'PK from AirTracksHistory received successfully : {last_air_track_pk}')
                        # ------------------------# ------------------------# -------------------
                        air_track.update({'AirTracksHistory': last_air_track_pk})
                        air_track.update(db.read_specific_field('CandidatesHistory', 'PrimaryMark',
                                                                {'CandidatesHistory': air_track['CandidatesHistory']}))
                        # a_tr_hist_pk_c = db.get_pk_tracks_hists({'CandidatesHistory': air_track['CandidatesHistory'],
                        #                                          'PrimaryMark': air_track['PrimaryMark'],
                        #                                          'AirTrack': air_track['AirTrack'],
                        #                                          'antennaId': air_track['antennaId']
                        #                                          })
                        # if a_tr_hist_pk_c == last_air_track_pk:
                        #     print('lol')
                        air_track.update(db.read_specific_field('CandidatesHistory', 'BeamTask',
                                                                {'CandidatesHistory': air_track['CandidatesHistory']}))
                        air_track.update(db.read_specific_field('CandidatesHistory', 'PrimaryMark',
                                                                {'CandidatesHistory': air_track['CandidatesHistory']}))
                        air_track.update(db.read_specific_field('BeamTasks', 'pulsePeriod',
                                                                {'BeamTask': air_track['BeamTask']}))
                        air_track.update(db.read_specific_field('PrimaryMarks', 'scanTime',
                                                                {'PrimaryMark': air_track['PrimaryMark']}))
                        db.update_air_tracks_histories(air_track)
        # ---------------------------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"----------------------------------- #
        for forbidden_sector in frame_reader.forbidden_sectors():
            x = frame_reader.entity_count
            console_log.info(f'\t\t\t\t\tForbiddenSector{x[0]}')
            del x[0]
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
        time_sec = "{:3.4f}".format(time.time() - start_frame_time)
        console_log.info(f"------------------------- {time_sec} seconds -------------------------\r\n\r\n")
    minutes = "{:3.2f}".format(float(time.time() - start_parsing_time) / 60)
    console_log.info(f"------------------------- {minutes} minutes -------------------------\r\n\r\n")
