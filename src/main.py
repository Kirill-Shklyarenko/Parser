import logging as log
import time
from pathlib import Path

from converter import DataBlocksReader
from data_base_methods import DataBase
from read_session_structure import read_session_structure
from read_session_telemetry import TelemetryFrameIterator

data_folder = Path(r'../data/session_01/')
planner = data_folder / r'Planner'
planner_rsf = data_folder / r'Planner.rsf'
logger = data_folder / r'logger.log'
dsn = 'dbname=Telemetry user=postgres password=123 host=localhost'


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
    structure = read_session_structure(planner)
    telemetry = TelemetryFrameIterator(planner_rsf, structure, 40000)
    data_base = DataBase(dsn)
    start_parsing_time = time.time()
    for frame in telemetry:
        start_frame_time = time.time()
        frame_reader = DataBlocksReader(frame)
        primary_marks_count = 1
        candidates_count = 1
        forbidden_sectors_count = 1
        # ---------------------------------ЗАПОЛНЯЕМ "BeamTasks"--------------------------------------- #
        for beam_task in frame_reader.beam_tasks():
            beam_task_pk = data_base.get_pk('BeamTasks', 'BeamTask', beam_task)
            if beam_task_pk is None:
                beam_task = data_base.map_bin_fields_to_table('BeamTasks', beam_task)
                data_base.insert_to_table('BeamTasks', beam_task)
            else:
                log.warning(f'BeamTask : already exists')
        # ---------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"------------------------------------ #
        for primary_mark in frame_reader.primary_marks():
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
        for candidate in frame_reader.candidates():
            log.info(f'Candidate {candidates_count}')
            log.info(f'Candidate state = {candidate["state"]}')
            if candidate['state'] != 0 and candidate['state'] != 3 \
                    and candidate['state'] != 5 and candidate['state'] != 6:
                beam_task_pk = data_base.get_pk('BeamTasks', 'BeamTask', candidate)
                if beam_task_pk:
                    candidate.update({'BeamTask': beam_task_pk})
                    pm_pk = data_base.get_pk('PrimaryMarks', 'PrimaryMark', candidate)
                    if pm_pk:
                        candidate.update({'PrimaryMark': pm_pk})
                        candidates_pk = data_base.get_pk('Candidates', 'Candidate', candidate)
                        # if dict_for_get_pk['id'] != 0:
                        if candidates_pk is None:
                            cand = data_base.map_bin_fields_to_table('Candidates', candidate)
                            data_base.insert_to_table('Candidates', cand)
                            candidates_pk = data_base.get_pk('Candidates', 'Candidate', candidate)
                        else:
                            log.warning(f'Candidate : already exists')
                        candidate.update({'Candidate': candidates_pk})
                        # candidate.update(dict_for_get_pk)
                        candidates_history_pk = data_base.get_pk('CandidatesHistory', 'CandidateHistory', candidate)
                        if candidates_history_pk is None:
                            candidate = data_base.map_bin_fields_to_table('CandidatesHistory', candidate)
                            data_base.insert_to_table('CandidatesHistory', candidate)
                        else:
                            log.warning(f'CandidateHistory : already exists')
                candidates_count += 1
        # ------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"--------------------------- #
        # for air_track in frame_reader.air_tracks():
        #     if air_track['antennaId'] != 0:
        #         get_pk_bt = {'trackId': 'id', 'taskType': 3, 'antennaId': 'antennaId'}
        #         get_pk_pm = {'BeamTask': 'BeamTask'}
        #         get_pk_candidate_hist = {'BeamTask': 'BeamTask'}
        #         get_pk_air_tracks = {'id': 'id'}
        #         get_pk_air_tracks_hist = {'AirTracksHistory': 'AirTracksHistory', 'PrimaryMark': 'PrimaryMark',
        #                                   'CandidateHistory': 'CandidateHistory', 'AirTrack': 'AirTrack'}
        #         pk_name = 'BeamTask'
        #         beam_task_pk = data_base.get_pk('BeamTasks', pk_name, air_track)
        #         if beam_task_pk:
        #             air_track.update(beam_task_pk)
        #             pk_name = 'PrimaryMark'
        #             pm_pk = data_base.get_pk('PrimaryMarks', pk_name, air_track)
        #             if pm_pk:
        #                 air_track.update(pm_pk)
        #                 pk_name = 'CandidatesHistory'
        #                 candidates_history_pk = data_base.get_pk('CandidatesHistory', pk_name, air_track)
        #                 if candidates_history_pk:
        #                     air_track.update(candidates_history_pk)
        #                     pk_name = 'AirTrack'
        #                     air_track_pk = data_base.get_pk('AirTracks', pk_name, air_track)
        #                     if air_track_pk is None:
        #                         data_base.insert_to_table('AirTracks', air_track)
        #                     else:
        #                         log.warning(f'{pk_name} : already exists')
        #                     air_track_pk = data_base.get_pk('AirTracks', pk_name, air_track)
        #                     if air_track_pk:
        #                         air_track.update(air_track_pk)
        #                         pk_name = 'AirTracksHistory'
        #                         air_track_history_pk = data_base.get_pk('AirTracksHistory', pk_name, air_track)
        #                         if air_track_history_pk is None:
        #                             air_track = data_base.map_bin_fields_to_table('AirTracksHistory', air_track)
        #                             data_base.insert_to_table('AirTracksHistory', air_track)
        #                         else:
        #                             log.warning(f'{pk_name} : already exists')
        # # --------------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"--------------------------------- #
        # for forbidden_sector in frame_reader.forbidden_sectors():
        #     log.info(f'PrimaryMark {forbidden_sectors_count}')
        #     get_pk_fs = {'azimuthBeginNSSK': 'azimuthBeginNSSK', 'azimuthEndNSSK': 'azimuthEndNSSK',
        #                  'elevationBeginNSSK': 'elevationBeginNSSK', 'elevationEndNSSK': 'elevationEndNSSK',
        #                  }
        #     pk_name = 'ForbiddenSector'
        #     fs_pk = data_base.get_pk('ForbiddenSectors', pk_name, forbidden_sector)
        #     if fs_pk is None:
        #         forbidden_sector = data_base.map_bin_fields_to_table('ForbiddenSectors', forbidden_sector)
        #         data_base.insert_to_table('ForbiddenSectors', forbidden_sector)
        #     else:
        #         log.warning(f'{pk_name} : already exists')
        # - FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN --- #
        time_sec = "{:7.4f}".format(time.time() - start_frame_time)
        log.info(f"--------------------{time_sec} seconds -----------------\r\n\r\n")

    time_sec = "{:7.4f}".format(time.time() - start_parsing_time)
    log.info(f"--------------------{time_sec} seconds -----------------\r\n\r\n")
