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
                    format='%(levelname)s : %(funcName)s: : %(message)s')  # %(lineno)d
    data_structure = StructureReader(planner)
    telemetry = TelemetryReader(planner_rsf, data_structure)
    data_base = DataBase(dsn)
    for frame in telemetry:  # (2237, 2838 - airTracks)
        # print(sys.getsizeof(frame))

        # candidate_q = {'candidatesQueueSize': 0}
        # track_candidate = {'state': 0}
        # tracks_q = {'tracksQueuesSize': 0}
        # rad_forbidden_sector = {'RadiationForbiddenSectorsCount': 0}
        # candidates_count = 0
        # tracks_count = 0
        # rad_forbidden_count = 0
        start_time = time.time()
        frame_handler = FrameHandler(frame, dsn)
        # ---------------------------------ЗАПОЛНЯЕМ "BeamTasks"--------------------------------------- #
        for beam in frame_handler.beam_task():
            columns_for_get_pk = ['taskId', 'antennaId']
            beam_task_pk = frame_handler.get_pk('BeamTasks', beam, columns_for_get_pk)
            if beam_task_pk is None:
                data_base.insert_to('BeamTasks', beam)

        # ---------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"-------------------------------- # 643 5283
        for primary_mark in frame_handler.primary_mark():
            columns_for_get_pk = ['taskId', 'antennaId', 'taskType']
            beam_task_pk = frame_handler.get_pk('BeamTasks', primary_mark, columns_for_get_pk)
            if beam_task_pk:
                primary_mark.update(beam_task_pk)
                columns_for_get_pk = ['BeamTask', 'PrimaryMark']
                primary_mark_pk = frame_handler.get_pk('PrimaryMarks', primary_mark, columns_for_get_pk)
                if primary_mark_pk is None:
                    data_base.insert_to('PrimaryMarks', primary_mark)
        #     # -----------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"---------------------- #
        #     elif re.search(r'TrackCandidates', frame[0]):
        #         frame.pop(0)
        #         candidate_q = {}
        #         for c in frame:
        #             candidate_q.update(c)
        #
        #     elif candidates_count < candidate_q['candidatesQueueSize']:
        #         if re.search(r'trackCandidate', frame[0]):
        #             frame.pop(0)
        #             track_candidate = {}
        #             for c in frame:
        #                 track_candidate.update(c)
        #
        #         # ---------------------------ЗАПОЛНЯЕМ "CandidatesHistory"----------------------------- #
        #         elif re.search(r'viewSpot', frame[0]):
        #             frame.pop(0)
        #             view_spot = {}
        #             for c in frame:
        #                 view_spot.update(c)
        #
        #         elif re.search(r'distanceResolutionSpot', frame[0]):
        #             frame.pop(0)
        #             distance_res_spot = {}
        #             for c in frame:
        #                 distance_res_spot.update(c)
        #
        #         elif re.search(r'velocityResolutionSpot', frame[0]):
        #             candidates_queue_size = candidate_q['candidatesQueueSize']
        #             candidates_count += 1
        #             print(f'\r\n\r\ncandidatesQueueSize == {candidates_count} / {candidates_queue_size}')
        #             print('c_state == ', track_candidate['state'])
        #
        #             frame.pop(0)
        #             velocity_res_spot = {}
        #             for c in frame:
        #                 velocity_res_spot.update(c)
        #             # ---------------------------ЗАПОЛНЯЕМ "Candidates"-------------------------------- #
        #             candidates_ids = {}
        #             candidates_ids.update({'id': track_candidate['id']})
        #
        #             # Проверка существует ли запись с такими параметрами
        #             candidates_ids = data_base.prepare_data_for_db('Candidates', candidates_ids)
        #             candidates_pk = data_base.read_from('Candidates', candidates_ids, ['id'])
        #             if candidates_pk is None:
        #                 data_base.insert_to('Candidates', candidates_ids)
        #
        #             candidates = {}
        #             # -----------------------------------state == 0------------------------------------ #
        #             if track_candidate['state'] == 0 or track_candidate['state'] == 3 or track_candidate['state'] == 5:
        #                 breakpoint()
        #             # -----------------------------------state == 1------------------------------------ #
        #             elif track_candidate['state'] == 1:  # frame 2687
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
        #             # -----------------------------------state == 2------------------------------------ #
        #             elif track_candidate['state'] == 2:  # frame 2689
        #                 candidates.update(distance_res_spot)
        #                 except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
        #                 candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
        #                 query_for_bt = ['taskId',
        #                                 'antennaId',
        #                                 'threshold',
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
        #             # -----------------------------------state == 4------------------------------------ # 4866
        #             elif track_candidate['state'] == 4:
        #                 candidates.update(velocity_res_spot)
        #                 except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
        #                 candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
        #                 query_for_bt = ['taskId',
        #                                 'antennaId',
        #                                 'threshold',
        #                                 'pulsePeriod'
        #                                 ]
        #                 bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
        #                 if bt_pk:
        #                     candidates.update({'BeamTask': bt_pk['BeamTask']})
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
        log.info(f"--------------------{time_sec} seconds ---------------\r\n\r\n")
        # print(f"\r\n--------------{time_sec} seconds --------------")
