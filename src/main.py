from text_file_reader import *
from bin_file_reader import *
from data_base_methods import *
from pathlib import Path
import time

data_folder = Path(r'../data/session_00/')
planner = data_folder / r'Planner'
planner_rsf = data_folder / r'Planner.rsf'
frame_rate_file = data_folder / r'frame_rate'
dsn = 'dbname=Telemetry user=postgres password=123 host=localhost'


if __name__ == "__main__":
    data_structure, frame_size = parse_text_file()
    start_frame = read_start_frame(frame_rate_file)
    frames_count = frame_counter(planner_rsf, frame_size)

    data_base = DB(dsn)
    data_base.connection()

    for frame_number in range(start_frame, frames_count):  # (2237, 2838 - airTracks)
        start_time = time.time()
        read_start_frame(frame_rate_file, frame_number)
        print(f"\r\n\r\n\r\n--------------- FRAME № {frame_number} ---------------")
        data = parse_bin_file(planner_rsf, data_structure, frame_size, frame_number)

        scan_data = {'primaryMarksCount': 0}
        candidate_q = {'candidatesQueueSize': 0}
        track_candidate = {'state': 0}
        tracks_q = {'tracksQueuesSize': 0}
        rad_forbidden_sector = {'RadiationForbiddenSectorsCount': 0}
        primary_marks_count = 0
        candidates_count = 0
        tracks_count = 0
        rad_forbidden_count = 0

        for index, group in enumerate(data):
            # ---------------------------------ЗАПОЛНЯЕМ "BeamTasks"----------------------------------- #

            if re.search(r'\bTask\b', group[0]):
                group.pop(0)
                task = {}
                for c in group:
                    task.update(c)

            elif re.search(r'beamTask', group[0]):
                group.pop(0)
                beam_task = {}
                beam_task.update(task)
                for c in group:
                    beam_task.update(c)
                print('Task_type == ', beam_task['taskType'])
                # Проверка существует ли запись с такими параметрами
                beam_task = data_base.prepare_data_for_db('BeamTasks', beam_task)
                bt_data = data_base.read_from('BeamTasks', beam_task, ['taskId', 'antennaId'])
                if bt_data is None:
                    data_base.insert_data_to_db('BeamTasks', beam_task)

            # ---------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"-------------------------------- # 643 5283
            elif re.search(r'scanData', group[0]):
                group.pop(0)
                scan_data = {}
                for c in group:
                    scan_data.update(c)

            elif primary_marks_count < scan_data['primaryMarksCount']:
                if re.search(r'primaryMark', group[0]):
                    group.pop(0)
                    primary_mark = {}
                    for c in group:
                        primary_mark.update(c)

                    primary_mark.update(scan_data)

                    primary_marks_size = scan_data['primaryMarksCount']
                    primary_marks_count += 1
                    print(f'\r\n\r\nprimaryMarksCount == {primary_marks_count} / {primary_marks_size}')
                    print('pM_type == ', primary_mark['type'])

                    bt_pk = data_base.read_from('BeamTasks', primary_mark, ['taskId',
                                                                       'antennaId',
                                                                       'taskType'
                                                                       ])
                    if bt_pk:
                        primary_mark.update({'BeamTask': bt_pk['BeamTask']})

                        # Проверка существует ли запись с такими параметрами
                        primary_mark = data_base.prepare_data_for_db('PrimaryMarks', primary_mark)
                        pm_data = data_base.read_from('PrimaryMarks', primary_mark, ['BeamTask'])
                        if pm_data is None:
                            data_base.insert_data_to_db('PrimaryMarks', primary_mark)

            # -----------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"---------------------- #
            elif re.search(r'TrackCandidates', group[0]):
                group.pop(0)
                candidate_q = {}
                for c in group:
                    candidate_q.update(c)

            elif candidates_count < candidate_q['candidatesQueueSize']:
                if re.search(r'trackCandidate', group[0]):
                    group.pop(0)
                    track_candidate = {}
                    for c in group:
                        track_candidate.update(c)

                # ---------------------------ЗАПОЛНЯЕМ "CandidatesHistory"----------------------------- #
                elif re.search(r'viewSpot', group[0]):
                    group.pop(0)
                    view_spot = {}
                    for c in group:
                        view_spot.update(c)

                elif re.search(r'distanceResolutionSpot', group[0]):
                    group.pop(0)
                    distance_res_spot = {}
                    for c in group:
                        distance_res_spot.update(c)

                elif re.search(r'velocityResolutionSpot', group[0]):
                    candidates_queue_size = candidate_q['candidatesQueueSize']
                    candidates_count += 1
                    print(f'\r\n\r\ncandidatesQueueSize == {candidates_count} / {candidates_queue_size}')
                    print('c_state == ', track_candidate['state'])

                    group.pop(0)
                    velocity_res_spot = {}
                    for c in group:
                        velocity_res_spot.update(c)
                    # ---------------------------ЗАПОЛНЯЕМ "Candidates"-------------------------------- #
                    candidates_ids = {}
                    candidates_ids.update({'id': track_candidate['id']})

                    # Проверка существует ли запись с такими параметрами
                    candidates_ids = data_base.prepare_data_for_db('Candidates', candidates_ids)
                    candidates_pk = data_base.read_from('Candidates', candidates_ids, ['id'])
                    if candidates_pk is None:
                        data_base.insert_data_to_db('Candidates', candidates_ids)

                    candidates = {}
                    # -----------------------------------state == 0------------------------------------ #
                    if track_candidate['state'] == 0 or track_candidate['state'] == 3 or track_candidate['state'] == 5:
                        breakpoint()
                    # -----------------------------------state == 1------------------------------------ #
                    elif track_candidate['state'] == 1:  # frame 2687
                        candidates.update(view_spot)
                        except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                        candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                        query_for_bt = ['taskId',
                                        'antennaId',
                                        'pulsePeriod'
                                        ]
                        bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates['betaBSK'] = candidates.pop('beamAzimuth')
                            candidates['epsilonBSK'] = candidates.pop('beamElevation')
                            query_for_pm = ['BeamTask',
                                            'azimuth', 'elevation',
                                            # 'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
                                    candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        data_base.insert_data_to_db('CandidatesHistory', candidates)
                    # -----------------------------------state == 2------------------------------------ #
                    elif track_candidate['state'] == 2:  # frame 2689
                        candidates.update(distance_res_spot)
                        except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                        candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                        query_for_bt = ['taskId',
                                        'antennaId',
                                        'threshold',
                                        'pulsePeriod'
                                        ]
                        bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates['betaBSK'] = candidates.pop('beamAzimuth')
                            candidates['epsilonBSK'] = candidates.pop('beamElevation')
                            query_for_pm = ['BeamTask',
                                            'azimuth', 'elevation',
                                            'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
                                    candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        data_base.insert_data_to_db('CandidatesHistory', candidates)
                    # -----------------------------------state == 4------------------------------------ # 4866
                    elif track_candidate['state'] == 4:
                        candidates.update(velocity_res_spot)
                        except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                        candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                        query_for_bt = ['taskId',
                                        'antennaId',
                                        'threshold',
                                        'pulsePeriod'
                                        ]
                        bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates['betaBSK'] = candidates.pop('beamAzimuth')
                            candidates['epsilonBSK'] = candidates.pop('beamElevation')
                            query_for_pm = ['BeamTask',
                                            'azimuth', 'elevation',
                                            # 'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
                                    candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        data_base.insert_data_to_db('CandidatesHistory', candidates)
                    # -----------------------------------state == 6------------------------------------ #
                    elif track_candidate['state'] == 6:
                        # --------------------------------view_spot------------------------------------ #
                        candidates.update(view_spot)
                        except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                        candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                        query_for_bt = ['taskId',
                                        'antennaId',
                                        'pulsePeriod'
                                        ]
                        bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})

                            candidates['betaBSK'] = candidates.pop('beamAzimuth')
                            candidates['epsilonBSK'] = candidates.pop('beamElevation')
                            query_for_pm = ['BeamTask',
                                            'azimuth', 'elevation',
                                            # 'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
                                    candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        data_base.insert_data_to_db('CandidatesHistory', candidates)

                        # ----------------------------distance_res_spot-------------------------------- #
                        candidates.update(track_candidate)
                        except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                        candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                        query_for_bt = ['taskId',
                                        'antennaId',
                                        'pulsePeriod'
                                        ]
                        bt_pk = data_base.read_from('BeamTasks', candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates['betaBSK'] = candidates.pop('beamAzimuth')
                            candidates['epsilonBSK'] = candidates.pop('beamElevation')
                            query_for_pm = ['BeamTask',
                                            'azimuth', 'elevation',
                                            'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = data_base.read_from('PrimaryMarks', candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = data_base.read_from('Candidates', candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = data_base.prepare_data_for_db('CandidatesHistory', candidates)
                                    candidates_history_pk = data_base.read_from('CandidatesHistory', candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        data_base.insert_data_to_db('CandidatesHistory', candidates)

            # ---------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"-------------------- # 2839frame
            elif re.search(r'\bTracks\b', group[0]):
                group.pop(0)
                tracks_q = {}
                for c in group:
                    tracks_q.update(c)

            elif tracks_count < tracks_q['tracksQueuesSize']:
                if re.search('track_', group[0]):
                    tracks_size = tracks_q['tracksQueuesSize']
                    tracks_count += 1
                    print(f'\r\n\r\ntracksQueuesSize == {tracks_count} / {tracks_size}')

                    group.pop(0)
                    track = {}
                    for c in group:
                        track.update(c)

                    print('t_type == ', track['type'])
                    # ----------------------------ЗАПОЛНЯЕМ "AirTracks"-------------------------------- #
                    air_tracks_ids = {}
                    air_tracks_ids.update({'id': track['id']})

                    # Проверка существует ли запись с такими параметрами
                    air_tracks_pk = data_base.read_from('AirTracks', air_tracks_ids, ['id'])
                    if air_tracks_pk is None:
                        data_base.insert_data_to_db('AirTracks', air_tracks_ids)
                    # ---------------------------ЗАПОЛНЯЕМ "AirTracksHistory"-------------------------- # 2839
                    query_for_pm = ['azimuth', 'elevation',
                                    # 'distance'
                                    # 'type',
                                    # 'antennaId',
                                    ]
                    pm_pk = data_base.read_from('PrimaryMarks', track, query_for_pm)
                    if pm_pk:
                        track.update({'PrimaryMark': pm_pk['PrimaryMark']})
                        query_for_candidates_history = ['PrimaryMark',
                                                        # 'azimuth', 'elevation',
                                                        # 'antennaId',
                                                        'betaBSK', 'epsilonBSK'
                                                        ]
                        candidates_history_pk = data_base.read_from('CandidatesHistory', track, query_for_candidates_history)
                        if candidates_history_pk:
                            track.update({'CandidatesHistory': candidates_history_pk['CandidatesHistory']})
                            air_tracks_pk = data_base.read_from('AirTracks', air_tracks_ids, ['id'])
                            track.update({'AirTrack': air_tracks_pk['AirTrack']})

                            # Проверка существует ли запись с такими параметрами
                            track = data_base.prepare_data_for_db('AirTracksHistory', track)
                            query_for_tracks_history = ['PrimaryMark',
                                                        'CandidatesHistory',
                                                        'AirTrack',
                                                        ]
                            air_tracks_history_pk = data_base.read_from('AirTracksHistory', track, query_for_tracks_history)
                            if air_tracks_history_pk is None:
                                data_base.insert_data_to_db('AirTracksHistory', track)
            # ----------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"--------------------------------- #
            elif re.search(r'\bRadiationForbiddenSectors\b', group[0]):
                group.pop(0)
                rad_forbidden_sector = {}
                for c in group:
                    rad_forbidden_sector.update(c)

            elif rad_forbidden_count < rad_forbidden_sector['RadiationForbiddenSectorsCount']:
                rad_forbidden_size = rad_forbidden_sector['RadiationForbiddenSectorsCount']
                rad_forbidden_count += 1
                print(f'primaryMarksCount == {rad_forbidden_count} / {rad_forbidden_size}')

                if re.search(r'RadiationForbiddenSector', group[0]):
                    for c in group:
                        rad_forbidden_sector.update(c)

                    # Проверка существует ли запись с такими параметрами
                    rad_forbidden_sector = data_base.prepare_data_for_db('ForbiddenSectors', rad_forbidden_sector)
                    rad_fs_pk = data_base.read_from('ForbiddenSectors', rad_forbidden_sector,
                                          ['azimuthBeginNSSK', 'azimuthEndNSSK',
                                           'elevationBeginNSSK', 'elevationEndNSSK'
                                           ])
                    if rad_fs_pk is None:
                        data_base.insert_data_to_db('ForbiddenSectors', rad_forbidden_sector)

        time_sec = "{:7.4f}".format(time.time() - start_time)
        print(f"\r\n--------------{time_sec} seconds --------------")
