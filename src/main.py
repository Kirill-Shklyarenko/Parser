import time
from pathlib import Path

from bin_file_reader import *
from data_base_methods import *
from text_file_reader import *

data_folder = Path(r'../data/session_01/')
planner = data_folder / r'Planner'
planner_rsf = data_folder / r'Planner.rsf'
logger = data_folder / r'logger.log'
dsn = 'dbname=Telemetry user=postgres password=123 host=localhost'
frame_number = 299


if __name__ == "__main__":
    """
    reg expr for Ideolog:
    message pattern:         ^(\d{2}:\d{2}:\d{2})\s(.*)\s\d{2}\s\s\w*\s\s(.*)$
    message start pattern:   ^\d
    time format:             HH:mm:SS
    groups: 
                             1
                             3
                             2
    
    """
    log.basicConfig(level=log.DEBUG,
                    format='%(asctime)s %(levelname)-7s %(lineno)-3s %(funcName)-16s %(message)s',
                    datefmt='%H:%m:%S',
                    filename=logger,
                    filemode='w')
    data_structure = StructureReader(planner)
    telemetry = TelemetryReader(planner_rsf, data_structure)
    data_base = DataBase(dsn)
    start_time_of_parsing = time.time()
    for frame in telemetry:
        start_frame_time = time.time()
        frame_handler = FrameHandler(frame)
        primary_marks_count = 1
        candidates_count = 1
        forbidden_sectors_count = 1
        # ---------------------------------ЗАПОЛНЯЕМ "BeamTasks"--------------------------------------- #
        for beam_task in frame_handler.beam_tasks():
            beam_task_pk = data_base.get_pk('BeamTasks', 'BeamTask', beam_task)
            if beam_task_pk is None:
                beam_task = data_base.map_bin_fields_to_table('BeamTasks', beam_task)
                data_base.insert_to_table('BeamTasks', beam_task)
            else:
                log.warning(f'BeamTask : already exists')
        # ---------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"------------------------------------ #
        for primary_mark in frame_handler.primary_marks():
            log.info(f'PrimaryMark {primary_marks_count}')
            log.info(f'PrimaryMark type = {primary_mark["markType"]}')
            beam_task_pk = data_base.get_pk('BeamTasks', 'BeamTask', primary_mark)
            if beam_task_pk:
                primary_mark.update({'BeamTask': beam_task_pk})
                primary_mark_pk = data_base.get_pk('PrimaryMarks', 'PrimaryMark', primary_mark)
                if primary_mark_pk is None:
                    primary_mark = data_base.map_bin_fields_to_table('PrimaryMarks', primary_mark)
                    data_base.insert_to_table('PrimaryMarks', primary_mark)
                else:
                    log.warning(f'PrimaryMark : already exists')
            primary_marks_count += 1
        # -----------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"-------------------------- #
        for candidate in frame_handler.candidates():
            log.info(f'Candidate {candidates_count}')
            log.info(f'Candidate state = {candidate["state"]}')
            if candidate['state'] != 0 and candidate['state'] != 3 \
                    and candidate['state'] != 5 and candidate['state'] != 6:
                get_pk_bt = {'taskId': 'taskId', 'antennaId': 'antennaId',
                             'trackId': 'id',
                             # 'taskType': 2,
                             }
                get_pk_pm = {'BeamTask': 'BeamTask', 'primaryMarkId': 'primaryMarkId'}
                get_pk_candidate = {'id': 'id'}
                get_pk_candidate_hist = {'BeamTask': 'BeamTask', 'PrimaryMark': 'PrimaryMark'}
                pk_name = 'BeamTask'
                dict_for_get_pk = data_base.map_table_fields_to_table(candidate, get_pk_bt)
                beam_task_pk = data_base.get_pk('BeamTasks', pk_name, dict_for_get_pk)
                if beam_task_pk:
                    candidate.update(beam_task_pk)
                    pk_name = 'PrimaryMark'
                    dict_for_get_pk = data_base.map_table_fields_to_table(candidate, get_pk_pm)
                    pm_pk = data_base.get_pk('PrimaryMarks', pk_name, dict_for_get_pk)
                    if pm_pk:
                        candidate.update(pm_pk)
                        pk_name = 'Candidate'
                        dict_for_get_pk = data_base.map_table_fields_to_table(candidate, get_pk_candidate)
                        candidates_pk = data_base.get_pk('Candidates', pk_name, dict_for_get_pk)
                        # if dict_for_get_pk['id'] != 0:
                        if candidates_pk is None:
                            data_base.insert_to_table('Candidates', dict_for_get_pk)
                            candidates_pk = data_base.get_pk('Candidates', pk_name, dict_for_get_pk)
                        else:
                            log.warning(f'{pk_name} : already exists')
                        candidate.update(candidates_pk)
                        pk_name = 'CandidateHistory'
                        dict_for_get_pk = data_base.map_table_fields_to_table(candidate, get_pk_candidate_hist)
                        candidate.update(dict_for_get_pk)
                        candidates_history_pk = data_base.get_pk('CandidatesHistory', pk_name, dict_for_get_pk)
                        if candidates_history_pk is None:
                            candidate = data_base.map_bin_fields_to_table('CandidatesHistory', candidate)
                            data_base.insert_to_table('CandidatesHistory', candidate)
                        else:
                            log.warning(f'{pk_name} : already exists')
                candidates_count += 1
        # ------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"--------------------------- #
        for air_track in frame_handler.air_tracks():
            if air_track['antennaId'] != 0:
                get_pk_bt = {'trackId': 'id', 'taskType': 3, 'antennaId': 'antennaId'}
                get_pk_pm = {'BeamTask': 'BeamTask'}
                get_pk_candidate_hist = {'BeamTask': 'BeamTask'}
                get_pk_air_tracks = {'id': 'id'}
                get_pk_air_tracks_hist = {'AirTracksHistory': 'AirTracksHistory', 'PrimaryMark': 'PrimaryMark',
                                          'CandidateHistory': 'CandidateHistory', 'AirTrack': 'AirTrack'}
                pk_name = 'BeamTask'
                dict_for_get_pk = data_base.map_table_fields_to_table(air_track, get_pk_bt)
                beam_task_pk = data_base.get_pk('BeamTasks', pk_name, dict_for_get_pk)
                if beam_task_pk:
                    air_track.update(beam_task_pk)
                    pk_name = 'PrimaryMark'
                    dict_for_get_pk = data_base.map_table_fields_to_table(air_track, get_pk_pm)
                    pm_pk = data_base.get_pk('PrimaryMarks', pk_name, dict_for_get_pk)
                    if pm_pk:
                        air_track.update(pm_pk)
                        pk_name = 'CandidatesHistory'
                        dict_for_get_pk = data_base.map_table_fields_to_table(air_track, get_pk_candidate_hist)
                        candidates_history_pk = data_base.get_pk('CandidatesHistory', pk_name, dict_for_get_pk)
                        if candidates_history_pk:
                            air_track.update(candidates_history_pk)
                            pk_name = 'AirTrack'
                            dict_for_get_pk = data_base.map_table_fields_to_table(air_track, get_pk_air_tracks)
                            air_track_pk = data_base.get_pk('AirTracks', pk_name, dict_for_get_pk)
                            if air_track_pk is None:
                                data_base.insert_to_table('AirTracks', dict_for_get_pk)
                            else:
                                log.warning(f'{pk_name} : already exists')
                            air_track_pk = data_base.get_pk('AirTracks', pk_name, dict_for_get_pk)
                            if air_track_pk:
                                air_track.update(air_track_pk)
                                pk_name = 'AirTracksHistory'
                                dict_for_get_pk = data_base.map_table_fields_to_table(air_track, get_pk_air_tracks_hist)
                                air_track_history_pk = data_base.get_pk('AirTracksHistory', pk_name, dict_for_get_pk)
                                if air_track_history_pk is None:
                                    air_track = data_base.map_bin_fields_to_table('AirTracksHistory', air_track)
                                    data_base.insert_to_table('AirTracksHistory', air_track)
                                else:
                                    log.warning(f'{pk_name} : already exists')
        # --------------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"--------------------------------- #
        for forbidden_sector in frame_handler.forbidden_sectors():
            log.info(f'PrimaryMark {forbidden_sectors_count}')
            get_pk_fs = {'azimuthBeginNSSK': 'azimuthBeginNSSK', 'azimuthEndNSSK': 'azimuthEndNSSK',
                         'elevationBeginNSSK': 'elevationBeginNSSK', 'elevationEndNSSK': 'elevationEndNSSK',
                         }
            dict_for_get_pk = data_base.map_table_fields_to_table(forbidden_sector, get_pk_fs)
            pk_name = 'ForbiddenSector'
            fs_pk = data_base.get_pk('ForbiddenSectors', pk_name, dict_for_get_pk)
            if fs_pk is None:
                forbidden_sector = data_base.map_bin_fields_to_table('ForbiddenSectors', forbidden_sector)
                data_base.insert_to_table('ForbiddenSectors', forbidden_sector)
            else:
                log.warning(f'{pk_name} : already exists')
        # - FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN --- #
        time_sec = "{:7.4f}".format(time.time() - start_frame_time)
        log.info(f"--------------------{time_sec} seconds -----------------\r\n\r\n")

    time_sec = "{:7.4f}".format(time.time() - start_time_of_parsing)
    log.info(f"--------------------{time_sec} seconds -----------------\r\n\r\n")
