from text_file_reader import *
from bin_file_reader import *
from data_base_methods import *
import time

planner = r'../data/session_00/Planner'
planner_rsf = r'../data/session_00/Planner.rsf'
start_frame = 5327  # 5395

if __name__ == "__main__":
    data_structure, frame_size = parse_text_file()
    frames_count = frame_counter(planner_rsf, frame_size)
    cur, conn = connection()
    for frame_number in range(start_frame, frames_count):  # (2237, 2838 - airTracks)
        start_time = time.time()
        print('\r\n\r\n\r\n\r\n        FRAME № %s \r\n' % frame_number)
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

                # Проверка существует ли запись с такими параметрами
                beam_task = prepare_data_for_db('BeamTasks', cur, beam_task)
                bt_data = read_from('BeamTasks', cur, beam_task, ['taskId', 'antennaId'])
                if bt_data is None:
                    insert_data_to_db('BeamTasks', cur, beam_task)

            # ---------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"-------------------------------- # 643 5283
            elif re.search(r'scanData', group[0]):
                group.pop(0)
                scan_data = {}
                for c in group:
                    scan_data.update(c)

            elif primary_marks_count < scan_data['primaryMarksCount']:
                primary_marks_size = scan_data['primaryMarksCount']
                print(f'primaryMarksCount == {primary_marks_size}')
                primary_marks_count += 1

                if re.search(r'primaryMark', group[0]):
                    group.pop(0)
                    primary_mark = {}
                    for c in group:
                        primary_mark.update(c)

                    primary_mark.update(scan_data)

                    if primary_mark['type'] == 0:
                        breakpoint()
                        print('markType == 0')
                    else:
                        print('markType == 1')

                        bt_pk = read_from('BeamTasks', cur, primary_mark, ['taskId',
                                                                           'antennaId',
                                                                           'taskType'
                                                                           ])
                        if bt_pk:
                            primary_mark.update({'BeamTask': bt_pk['BeamTask']})

                            # Проверка существует ли запись с такими параметрами
                            primary_mark = prepare_data_for_db('PrimaryMarks', cur, primary_mark)
                            pm_data = read_from('PrimaryMarks', cur, primary_mark, ['BeamTask'])
                            if pm_data is None:
                                insert_data_to_db('PrimaryMarks', cur, primary_mark)

            # -----------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"---------------------- #
            elif re.search(r'TrackCandidates', group[0]):
                group.pop(0)
                candidate_q = {}
                for c in group:
                    candidate_q.update(c)

            elif candidates_count < candidate_q['candidatesQueueSize']:
                # ---------------------------ЗАПОЛНЯЕМ "Candidates"------------------------------------ #
                if re.search(r'trackCandidate', group[0]):
                    group.pop(0)
                    track_candidate = {}
                    for c in group:
                        track_candidate.update(c)
                    # breakpoint()

                    candidates_ids = {}
                    candidates_ids.update({'id': track_candidate['id']})

                    # Проверка существует ли запись с такими параметрами
                    candidates_ids = prepare_data_for_db('Candidates', cur, candidates_ids)
                    candidates_pk = read_from('Candidates', cur, candidates_ids, ['id'])
                    if candidates_pk is None:
                        insert_data_to_db('Candidates', cur, candidates_ids)

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
                    print(f'candidatesQueueSize == {candidates_queue_size}')
                    candidates_count += 1

                    group.pop(0)
                    velocity_res_spot = {}
                    for c in group:
                        velocity_res_spot.update(c)

                    # breakpoint()
                    candidates = {}
                    except_keys = ['taskId', 'beamAzimuth', 'beamElevation']
                    candidates.update({k: v for k, v in track_candidate.items() if k not in except_keys})
                    # -----------------------------------state == 0------------------------------------ #
                    if candidates['state'] == 0:
                        breakpoint()
                        print('candidates_state == 0')
                    # -----------------------------------state == 1------------------------------------ #
                    elif candidates['state'] == 1:  # frame 2687
                        print('candidates_state == 1')
                        candidates.update(view_spot)
                        query_for_bt = ['taskId', 'antennaId', 'pulsePeriod']
                        bt_pk = read_from('BeamTasks', cur, candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates.update(track_candidate)
                            candidates['betaBSK'] = candidates.pop('azimuth')
                            candidates['epsilonBSK'] = candidates.pop('elevation')
                            query_for_pm = ['BeamTask',
                                            # 'azimuth', 'elevation',
                                            'beamAzimuth', 'beamElevation'
                                            ]
                            pm_pk = read_from('PrimaryMarks', cur, candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})

                                candidates_pk = read_from('Candidates', cur, candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = prepare_data_for_db('CandidatesHistory', cur, candidates)
                                    candidates_history_pk = read_from('CandidatesHistory', cur, candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        insert_data_to_db('CandidatesHistory', cur, candidates)
                    # -----------------------------------state == 2------------------------------------ #
                    elif candidates['state'] == 2:  # frame 2689
                        print('candidates_state == 2')
                        candidates.update(track_candidate)
                        candidates.update(distance_res_spot)
                        query_for_bt = ['taskId', 'antennaId', 'pulsePeriod']
                        bt_pk = read_from('BeamTasks', cur, candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates['betaBSK'] = candidates.pop('azimuth')
                            candidates['epsilonBSK'] = candidates.pop('elevation')
                            query_for_pm = ['BeamTask',
                                            # 'azimuth', 'elevation',
                                            'beamAzimuth', 'beamElevation'
                                            ]

                            pm_pk = read_from('PrimaryMarks', cur, candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = read_from('Candidates', cur, candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = prepare_data_for_db('CandidatesHistory', cur, candidates)
                                    candidates_history_pk = read_from('CandidatesHistory', cur, candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        insert_data_to_db('CandidatesHistory', cur, candidates)
                    # -----------------------------------state == 3------------------------------------ #
                    elif candidates['state'] == 3:
                        breakpoint()
                        print('candidates_state == 3')
                    # -----------------------------------state == 4------------------------------------ # 4866
                    elif candidates['state'] == 4:
                        print('candidates_state == 4')
                        candidates.update(velocity_res_spot)
                        query_for_bt = ['taskId',
                                        'antennaId',
                                        'threshold',
                                        'pulsePeriod'
                                        ]
                        bt_pk = read_from('BeamTasks', cur, candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            query_for_pm = [
                                            'BeamTask',
                                            'distance',
                                            # 'azimuth', 'elevation',
                                            'betaBSK', 'epsilonBSK'
                                            ]
                            pm_pk = read_from('PrimaryMarks', cur, candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = read_from('Candidates', cur, candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = prepare_data_for_db('CandidatesHistory', cur, candidates)
                                    candidates_history_pk = read_from('CandidatesHistory', cur, candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        insert_data_to_db('CandidatesHistory', cur, candidates)
                    # -----------------------------------state == 5------------------------------------ #
                    elif candidates['state'] == 5:
                        # breakpoint()
                        print('candidates_state == 5')
                    # -----------------------------------state == 6------------------------------------ #
                    elif candidates['state'] == 6:
                        print('candidates_state == 6')
                        # --------------------------------view_spot------------------------------------ #
                        candidates.update(view_spot)
                        query_for_bt = ['taskId', 'antennaId', 'pulsePeriod']
                        bt_pk = read_from('BeamTasks', cur, candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates.update(track_candidate)
                            candidates['betaBSK'] = candidates.pop('azimuth')
                            candidates['epsilonBSK'] = candidates.pop('elevation')
                            query_for_pm = ['BeamTask',
                                            # 'azimuth', 'elevation',
                                            'beamAzimuth', 'beamElevation'
                                            ]
                            pm_pk = read_from('PrimaryMarks', cur, candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})

                                candidates_pk = read_from('Candidates', cur, candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = prepare_data_for_db('CandidatesHistory', cur, candidates)
                                    candidates_history_pk = read_from('CandidatesHistory', cur, candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        insert_data_to_db('CandidatesHistory', cur, candidates)

                        # ----------------------------distance_res_spot-------------------------------- #
                        candidates.update(track_candidate)
                        candidates.update(distance_res_spot)
                        query_for_bt = ['taskId', 'antennaId',
                                        'pulsePeriod',
                                        ]
                        bt_pk = read_from('BeamTasks', cur, candidates, query_for_bt)
                        if bt_pk:
                            candidates.update({'BeamTask': bt_pk['BeamTask']})
                            candidates['betaBSK'] = candidates.pop('azimuth')
                            candidates['epsilonBSK'] = candidates.pop('elevation')
                            query_for_pm = ['BeamTask',
                                            # 'azimuth', 'elevation',
                                            'beamAzimuth', 'beamElevation',
                                            ]
                            pm_pk = read_from('PrimaryMarks', cur, candidates, query_for_pm)
                            if pm_pk:
                                candidates.update({'PrimaryMark': pm_pk['PrimaryMark']})
                                candidates_pk = read_from('Candidates', cur, candidates, ['id'])
                                if candidates_pk:
                                    candidates.update({'Candidate': candidates_pk['Candidate']})

                                    # Проверка существует ли запись с такими параметрами
                                    candidates = prepare_data_for_db('CandidatesHistory', cur, candidates)
                                    candidates_history_pk = read_from('CandidatesHistory', cur, candidates,
                                                                      ['BeamTask', 'PrimaryMark', 'Candidate'])
                                    if candidates_history_pk is None:
                                        insert_data_to_db('CandidatesHistory', cur, candidates)

            # ---------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"-------------------- # 2839frame
            elif re.search(r'\bTracks\b', group[0]):
                group.pop(0)
                tracks_q = {}
                for c in group:
                    tracks_q.update(c)

            elif tracks_count < tracks_q['tracksQueuesSize']:
                # ---------------------------ЗАПОЛНЯЕМ "AirTracks"------------------------------------- #
                if re.search('track_', group[0]):
                    tracks_count += 1
                    group.pop(0)
                    track = {}
                    for c in group:
                        track.update(c)

                    # if track['antennaId'] != 0:     # and track['type'] != 0
                    #     breakpoint()
                    # ----------------------------ЗАПОЛНЯЕМ "AirTracks"-------------------------------- #
                    air_tracks_ids = {}
                    air_tracks_ids.update({'id': track['id']})

                    # Проверка существует ли запись с такими параметрами
                    air_tracks_pk = read_from('AirTracks', cur, air_tracks_ids, ['id'])
                    if air_tracks_pk is None:
                        insert_data_to_db('AirTracks', cur, air_tracks_ids)

                    # ---------------------------ЗАПОЛНЯЕМ "AirTracksHistory"-------------------------- # 2839

                    # track['betaBSK'] = track.pop('azimuth')
                    # track['epsilonBSK'] = track.pop('elevation')
                    query_for_pm = ['azimuth', 'elevation',
                                    # 'distance'
                                    # 'type',
                                    # 'antennaId',
                                    ]
                    pm_pk = read_from('PrimaryMarks', cur, track, query_for_pm)
                    if pm_pk:
                        track.update({'PrimaryMark': pm_pk['PrimaryMark']})
                        query_for_candidates_history = ['PrimaryMark',
                                                        # 'azimuth', 'elevation',
                                                        # 'antennaId',
                                                        'beamAzimuth', 'beamElevation'
                                                        ]
                        candidates_history_pk = read_from('CandidatesHistory', cur, track, query_for_candidates_history)
                        if candidates_history_pk:
                            track.update({'CandidatesHistory': candidates_history_pk['CandidatesHistory']})
                            air_tracks_pk = read_from('AirTracks', cur, air_tracks_ids, ['id'])
                            track.update({'AirTrack': air_tracks_pk['AirTrack']})

                            # Проверка существует ли запись с такими параметрами
                            track = prepare_data_for_db('AirTracksHistory', cur, track)
                            query_for_tracks_history = ['PrimaryMark',
                                                        'CandidatesHistory',
                                                        'AirTrack',
                                                        ]
                            air_tracks_history_pk = read_from('AirTracksHistory', cur, track, query_for_tracks_history)
                            if air_tracks_history_pk is None:
                                insert_data_to_db('AirTracksHistory', cur, track)

            # ----------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"--------------------------------- #
            elif re.search(r'\bRadiationForbiddenSectors\b', group[0]):
                group.pop(0)
                rad_forbidden_sector = {}
                for c in group:
                    rad_forbidden_sector.update(c)

            elif rad_forbidden_count < rad_forbidden_sector['RadiationForbiddenSectorsCount']:
                rad_forbidden_count += 1

                if re.search(r'RadiationForbiddenSector', group[0]):
                    for c in group:
                        rad_forbidden_sector.update(c)

                    # Проверка существует ли запись с такими параметрами
                    rad_forbidden_sector = prepare_data_for_db('ForbiddenSectors', cur, rad_forbidden_sector)
                    rad_fs_pk = read_from('ForbiddenSectors', cur, rad_forbidden_sector,
                                          ['azimuthBeginNSSK', 'azimuthEndNSSK',
                                           'elevationBeginNSSK', 'elevationEndNSSK'
                                           ])
                    if rad_fs_pk is None:
                        insert_data_to_db('ForbiddenSectors', cur, rad_forbidden_sector)

        time_sec = "{:7.4f}".format(time.time() - start_time)
        print(f"\r\n----- {time_sec} seconds  -----")
