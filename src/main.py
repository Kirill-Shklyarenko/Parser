from text_file_reader import *
from bin_file_reader import *
from data_base_methods import *
from pathlib import Path

import logging as log
import time

data_folder = Path(r'../data/session_00/')
planner = data_folder / r'Planner'
planner_rsf = data_folder / r'Planner.rsf'
logger = data_folder / r'logger.log'
dsn = 'dbname=Telemetry user=postgres password=123 host=localhost'


def map_fields_table_to_table(dict_from_telemetry: dict, formatter_dict: dict) -> dict:
    result = {}
    for fk, fv in dict_from_telemetry.items():
        if 'isFake' in fk:
            dict_from_telemetry[fk] = bool(dict_from_telemetry[fk])
        for sk, sv in formatter_dict.items():
            if fk == sv:
                result.update({sk: fv})
    formatter_dict.update(result)
    # formatter_dict.update(dict_from_telemetry)
    return formatter_dict


if __name__ == "__main__":
    log.basicConfig(filename=logger, filemode='w+', level=log.DEBUG,
                    format='%(levelname)s : %(lineno)d : %(funcName)s : %(message)s')  # %(lineno)d
    data_structure = StructureReader(planner)
    telemetry = TelemetryReader(planner_rsf, data_structure)
    data_base = DataBase(dsn)
    for frame in telemetry:  # (2237, 2838 - airTracks)
        # rad_forbidden_sector = {'RadiationForbiddenSectorsCount': 0}
        # rad_forbidden_count = 0
        start_time = time.time()
        frame_handler = FrameHandler(frame)
        # ---------------------------------ЗАПОЛНЯЕМ "BeamTasks"--------------------------------------- #
        for beam in frame_handler.beam_task():
            get_pk_bt = {'taskId': 'taskId', 'antennaId': 'antennaId'}
            dict_for_get_pk = map_fields_table_to_table(beam, get_pk_bt)
            pk_name = 'BeamTask'
            beam_task_pk = data_base.get_pk('BeamTasks', pk_name, dict_for_get_pk)
            if beam_task_pk is None:
                beam = data_base.map_fields_bin_to_table('BeamTasks', beam)
                data_base.insert_to('BeamTasks', beam)
            else:
                log.debug(f'BeamTask is already exists')

        # ---------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"------------------------------------ # 643 5283
        for primary_mark in frame_handler.primary_mark():
            get_pk_bt = {'taskId': 'taskId', 'antennaId': 'antennaId'}
            get_pk_pm = {'BeamTask': 'BeamTask', 'antennaId': 'antennaId'}
            dict_for_get_pk = map_fields_table_to_table(primary_mark, get_pk_bt)
            pk_name = 'BeamTask'
            beam_task_pk = data_base.get_pk('BeamTasks', pk_name, dict_for_get_pk)
            if beam_task_pk:
                primary_mark.update(beam_task_pk)
                dict_for_get_pk = map_fields_table_to_table(primary_mark, get_pk_pm)
                pk_name = 'PrimaryMark'
                primary_mark_pk = data_base.get_pk('PrimaryMarks', pk_name, dict_for_get_pk)
                if primary_mark_pk is None:
                    primary_mark = data_base.map_fields_bin_to_table('PrimaryMarks', primary_mark)
                    data_base.insert_to('PrimaryMarks', primary_mark)
                else:
                    log.debug(f'PrimaryMark is already exists')

        #     # -----------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"-------------------- #
        for candidate in frame_handler.candidate():
            if candidate['state'] != 0 and candidate['state'] != 3 \
                    and candidate['state'] != 5 and candidate['state'] != 6:
                get_pk_bt = {'taskId': 'taskId', 'trackId': 'id', 'taskType': 2, 'antennaId': 'antennaId'}
                get_pk_pm = {'BeamTask': 'BeamTask', 'taskId': 'taskId', 'antennaId': 'antennaId'}
                get_pk_candidate = {'id': 'id'}
                get_pk_candidate_hist = {'BeamTask': 'BeamTask', 'PrimaryMark': 'PrimaryMark', 'Candidate': 'Candidate'}

                pk_name = 'BeamTask'
                dict_for_get_pk = map_fields_table_to_table(candidate, get_pk_bt)
                beam_task_pk = data_base.get_pk('BeamTasks', pk_name, dict_for_get_pk)
                if beam_task_pk:
                    candidate.update(beam_task_pk)
                    pk_name = 'PrimaryMarks'
                    dict_for_get_pk = map_fields_table_to_table(candidate, get_pk_pm)
                    pm_pk = data_base.get_pk('PrimaryMarks', pk_name, dict_for_get_pk)
                    if pm_pk:
                        candidate.update(pm_pk)
                        pk_name = 'Candidate'
                        dict_for_get_pk = map_fields_table_to_table(candidate, get_pk_candidate)
                        candidates_pk = data_base.insert_to('Candidates', dict_for_get_pk)
                        candidates_pk = data_base.get_pk('Candidates', pk_name, candidates_pk)
                        candidate.update(candidates_pk)
                        pk_name = 'CandidateHistory'
                        dict_for_get_pk = map_fields_table_to_table(candidate, get_pk_candidate_hist)
                        candidates_history_pk = data_base.get_pk('CandidatesHistory', pk_name, dict_for_get_pk)
                        if candidates_history_pk is None:
                            candidate = data_base.map_fields_bin_to_table('CandidatesHistory', candidate)
                            data_base.insert_to('CandidatesHistory', candidate)
                        else:
                            log.debug(f'CandidatesHistory is already exists')
        # ---------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"------------------------ # 2839frame
        for air_track in frame_handler.air_track():
            get_pk_bt = {'trackId': 'id', 'taskType': 3, 'antennaId': 'antennaId'}
            get_pk_pm = {'BeamTask': 'BeamTask'}
            get_pk_candidate_hist = {'BeamTask': 'BeamTask'}
            get_pk_air_tracks = {'id': 'id'}
            get_pk_air_tracks_hist = {'AirTracksHistory': 'AirTracksHistory', 'PrimaryMark': 'PrimaryMark',
                                      'CandidateHistory': 'CandidateHistory', 'AirTrack': 'AirTrack'}
            pk_name = 'BeamTask'
            dict_for_get_pk = map_fields_table_to_table(air_track, get_pk_bt)
            beam_task_pk = data_base.get_pk('BeamTasks', pk_name, dict_for_get_pk)
            if beam_task_pk:
                air_track.update(beam_task_pk)
                pk_name = 'PrimaryMarks'
                dict_for_get_pk = map_fields_table_to_table(air_track, get_pk_pm)
                pm_pk = data_base.get_pk('PrimaryMarks', pk_name, dict_for_get_pk)
                if pm_pk:
                    air_track.update(pm_pk)
                    pk_name = 'CandidatesHistory'
                    dict_for_get_pk = map_fields_table_to_table(air_track, get_pk_candidate_hist)
                    candidates_history_pk = data_base.get_pk('CandidatesHistory', pk_name, dict_for_get_pk)
                    if candidates_history_pk:
                        air_track.update(candidates_history_pk)
                        pk_name = 'AirTrack'
                        dict_for_get_pk = map_fields_table_to_table(air_track, get_pk_air_tracks)
                        air_track_pk = data_base.get_pk('AirTracks', pk_name, dict_for_get_pk)
                        if air_track_pk is None:
                            data_base.insert_to('AirTracks', dict_for_get_pk)
                        air_track_pk = data_base.get_pk('AirTracks', pk_name, dict_for_get_pk)
                        if air_track_pk:
                            air_track.update(air_track_pk)
                            pk_name = 'AirTracksHistory'
                            dict_for_get_pk = map_fields_table_to_table(air_track, get_pk_air_tracks_hist)
                            air_track_history_pk = data_base.get_pk('AirTracksHistory', pk_name, dict_for_get_pk)
                            if candidates_history_pk is None:
                                air_track = data_base.map_fields_bin_to_table('AirTracksHistory', air_track)
                                data_base.insert_to('AirTracksHistory', air_track)
                            else:
                                log.debug(f'AirTracksHistory is already exists')
        #     # ----------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"--------------------------------- #
        #     elif re.search(r'\bRadiationForbiddenSectors\b', frame[0]):
        #         frame.pop(0)
        #         rad_forbidden_sector = {}
        #         for c in frame:
        #             rad_forbidden_sector.update(c)
        #
        #     elif rad_forbidden_count < rad_forbidden_sector['RadiationForbiddenSectorsCount']:
        #         rad_forbidden_size = rad_forbidden_sector['RadiationForbiddenSectorsCount']
        #         rad_forbidden_count += 1
        #         print(f'primaryMarksCount == {rad_forbidden_count} / {rad_forbidden_size}')
        #
        #         if re.search(r'RadiationForbiddenSector', frame[0]):
        #             for c in frame:
        #                 rad_forbidden_sector.update(c)
        #
        #             # Проверка существует ли запись с такими параметрами
        #             rad_forbidden_sector = data_base.prepare_data_for_db('ForbiddenSectors', rad_forbidden_sector)
        #             rad_fs_pk = data_base.read_from('ForbiddenSectors', rad_forbidden_sector,
        #                                   ['azimuthBeginNSSK', 'azimuthEndNSSK',
        #                                    'elevationBeginNSSK', 'elevationEndNSSK'
        #                                    ])
        #             if rad_fs_pk is None:
        #                 data_base.insert_to('ForbiddenSectors', rad_forbidden_sector)
        time_sec = "{:7.4f}".format(time.time() - start_time)
        log.warning(f"--------------------{time_sec} seconds ---------------\r\n\r\n")
        # print(f"\r\n--------------{time_sec} seconds --------------")
