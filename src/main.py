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

if __name__ == "__main__":
    log.basicConfig(filename=logger, filemode='w+', level=log.DEBUG,
                    format='%(levelname)s : %(lineno)d : %(funcName)s: : %(message)s')  # %(lineno)d
    data_structure = StructureReader(planner)
    telemetry = TelemetryReader(planner_rsf, data_structure)
    data_base = DataBase(dsn)
    for frame in telemetry:  # (2237, 2838 - airTracks)
        # print(sys.getsizeof(frame))

        # tracks_q = {'tracksQueuesSize': 0}
        # rad_forbidden_sector = {'RadiationForbiddenSectorsCount': 0}

        # tracks_count = 0
        # rad_forbidden_count = 0
        start_time = time.time()
        frame_handler = FrameHandler(frame, dsn)
        # ---------------------------------ЗАПОЛНЯЕМ "BeamTasks"--------------------------------------- #
        for beam in frame_handler.beam_task():
            columns_for_get_pk = ['taskId', 'antennaId']
            dict_for_get_pk = {k: v for k, v in beam.items() if k in columns_for_get_pk}
            pk_name = 'BeamTask'
            beam_task_pk = data_base.get_pk('BeamTasks', pk_name, dict_for_get_pk)
            if beam_task_pk is None:
                data_base.insert_to('BeamTasks', beam)
            else:
                log.debug(f'BeamTask : {beam_task_pk} is already exists')
        # ---------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"------------------------------------ # 643 5283
        for primary_mark in frame_handler.primary_mark():
            columns_for_get_pk = ['taskId', 'antennaId']
            pk_name = 'BeamTask'
            dict_for_get_pk = {k: v for k, v in primary_mark.items() if k in columns_for_get_pk}
            beam_task_pk = frame_handler.get_pk('BeamTasks', pk_name, dict_for_get_pk)
            if beam_task_pk:
                primary_mark.update(beam_task_pk)
                columns_for_get_pk = ['BeamTask', 'beamAzimuth', 'beamElevation']
                pk_name = 'PrimaryMark'
                dict_for_get_pk = {k: v for k, v in primary_mark.items() if k in columns_for_get_pk}
                primary_mark_pk = frame_handler.get_pk('PrimaryMarks', primary_mark, dict_for_get_pk)
                if primary_mark_pk is None:
                    data_base.insert_to('PrimaryMarks', primary_mark)
                else:
                    log.debug(f'PrimaryMark : {primary_mark_pk["PrimaryMark"]} is already exists')
        #     # -----------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"-------------------- #
        for candidate in frame_handler.candidate():
            if candidate['state'] == 1:
                get_pk_bt = ['taskId', 'antennaId']
                get_pk_pm = ['BeamTask', 'azimuth', 'elevation']
            elif candidate['state'] == 2:

            elif candidate['state'] == 4:

            pk_name = 'BeamTask'
            dict_for_get_pk = {k: v for k, v in candidate.items() if k in get_pk_bt}
            beam_task_pk = frame_handler.get_pk('BeamTasks', pk_name, dict_for_get_pk)
            if beam_task_pk:
                candidate.update(beam_task_pk)

                pk_name = 'PrimaryMarks'
                dict_for_get_pk = {k: v for k, v in candidate.items() if k in get_pk_pm}
                pm_pk = frame_handler.get_pk('PrimaryMarks', pk_name, dict_for_get_pk)
                if pm_pk:
                    candidate.update(pm_pk)
                    columns_for_get_pk = ['id']
                    pk_name = 'Candidate'
                    dict_for_get_pk = {k: v for k, v in candidate.items() if k in columns_for_get_pk}
                    candidates_pk = data_base.insert_to('Candidates', dict_for_get_pk)
                    candidate.update(candidates_pk)
                    columns_for_get_pk = ['BeamTask', 'PrimaryMark', 'Candidate']
                    pk_name = 'CandidateHistory'
                    dict_for_get_pk = {k: v for k, v in candidate.items() if k in columns_for_get_pk}
                    candidates_history_pk = data_base.read_from('CandidatesHistory', pk_name, dict_for_get_pk)
                    if candidates_history_pk is None:
                        data_base.insert_to('CandidatesHistory', candidate)











        #             # -----------------------------------state == 6------------------------------------ #
        #             elif track_candidate['state'] == 6:
        #                 # --------------------------------view_spot------------------------------------ #
        #                 candidates.update(view_spot)
        #                 except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
        #                 candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
        #                 query_for_bt = ['taskId',
        #                                 'antennaId',
        #                                 'pulsePeriod'
        #                                 ]
        #                 bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
        #                 if bt_pk:
        #                     candidates.update({'BeamTask': bt_pk['BeamTask']})
        #
        #                     candidates['betaBSK'] = candidates.pop('beamAzimuth')
        #                     candidates['epsilonBSK'] = candidates.pop('beamElevation')
        #                     query_for_pm = ['BeamTask',
        #                                     'azimuth', 'elevation',
        #                                     # 'betaBSK', 'epsilonBSK'
        #                                     ]
        #                     pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
        #                     if pm_pk:
        #                         candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
        #                         candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
        #                         if candidates_pk:
        #                             candidates.update({'Candidate': candidates_pk['Candidate']})
        #
        #                             # Проверка существует ли запись с такими параметрами
        #                             candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
        #                             candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
        #                                                               ['BeamTask', 'PrimaryMark', 'Candidate'])
        #                             if candidates_history_pk is None:
        #                                 data_base.insert_to('CandidatesHistory', candidates)
        #
        #                 # ----------------------------distance_res_spot-------------------------------- #
        #                 candidates.update(track_candidate)
        #                 except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
        #                 candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
        #                 query_for_bt = ['taskId',
        #                                 'antennaId',
        #                                 'pulsePeriod'
        #                                 ]
        #                 bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
        #                 if bt_pk:
        #                     candidates.update({'BeamTask': bt_pk['BeamTask']})
        #                     candidates['betaBSK'] = candidates.pop('beamAzimuth')
        #                     candidates['epsilonBSK'] = candidates.pop('beamElevation')
        #                     query_for_pm = ['BeamTask',
        #                                     'azimuth', 'elevation',
        #                                     'betaBSK', 'epsilonBSK'
        #                                     ]
        #                     pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
        #                     if pm_pk:
        #                         candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
        #                         candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
        #                         if candidates_pk:
        #                             candidates.update({'Candidate': candidates_pk['Candidate']})
        #
        #                             # Проверка существует ли запись с такими параметрами
        #                             candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
        #                             candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
        #                                                               ['BeamTask', 'PrimaryMark', 'Candidate'])
        #                             if candidates_history_pk is None:
        #                                 data_base.insert_to('CandidatesHistory', candidates)
        #
        #     # ---------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"-------------------- # 2839frame
        #     elif re.search(r'\bTracks\b', frame[0]):
        #         frame.pop(0)
        #         tracks_q = {}
        #         for c in frame:
        #             tracks_q.update(c)
        #
        #     elif tracks_count < tracks_q['tracksQueuesSize']:
        #         if re.search('track_', frame[0]):
        #             tracks_size = tracks_q['tracksQueuesSize']
        #             tracks_count += 1
        #             print(f'\r\n\r\ntracksQueuesSize == {tracks_count} / {tracks_size}')
        #
        #             frame.pop(0)
        #             track = {}
        #             for c in frame:
        #                 track.update(c)
        #
        #             print('t_type == ', track['type'])
        #             # ----------------------------ЗАПОЛНЯЕМ "AirTracks"-------------------------------- #
        #             air_tracks_ids = {}
        #             air_tracks_ids.update({'id': track['id']})
        #
        #             # Проверка существует ли запись с такими параметрами
        #             air_tracks_pk = data_base.read_from('AirTracks', air_tracks_ids, ['id'])
        #             if air_tracks_pk is None:
        #                 data_base.insert_to('AirTracks', air_tracks_ids)
        #             # ---------------------------ЗАПОЛНЯЕМ "AirTracksHistory"-------------------------- # 2839
        #             query_for_pm = ['azimuth', 'elevation',
        #                             # 'distance'
        #                             # 'type',
        #                             # 'antennaId',
        #                             ]
        #             pm_pk = data_base.read_from('PrimaryMarks', track, query_for_pm)
        #             if pm_pk:
        #                 track.update({'PrimaryMark': pm_pk['PrimaryMark']})
        #                 query_for_candidates_history = ['PrimaryMark',
        #                                                 # 'azimuth', 'elevation',
        #                                                 # 'antennaId',
        #                                                 'betaBSK', 'epsilonBSK'
        #                                                 ]
        #                 candidates_history_pk = data_base.read_from('CandidatesHistory', track, query_for_candidates_history)
        #                 if candidates_history_pk:
        #                     track.update({'CandidatesHistory': candidates_history_pk['CandidatesHistory']})
        #                     air_tracks_pk = data_base.read_from('AirTracks', air_tracks_ids, ['id'])
        #                     track.update({'AirTrack': air_tracks_pk['AirTrack']})
        #
        #                     # Проверка существует ли запись с такими параметрами
        #                     track = data_base.prepare_data_for_db('AirTracksHistory', track)
        #                     query_for_tracks_history = ['PrimaryMark',
        #                                                 'CandidatesHistory',
        #                                                 'AirTrack',
        #                                                 ]
        #                     air_tracks_history_pk = data_base.read_from('AirTracksHistory', track, query_for_tracks_history)
        #                     if air_tracks_history_pk is None:
        #                         data_base.insert_to('AirTracksHistory', track)
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
