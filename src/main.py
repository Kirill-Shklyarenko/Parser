from text_file_parser import *
from bin_file_parser import *
from data_base_methods import *
import time

if __name__ == "__main__":
    data_structure, frame_size = parse_text_file()
    frame_c = frame_counter(frame_size)
    cur, conn = connection()
    for frame_number in range(2923, frame_c):  # frame_number = (300 - Candidates); (2237, 2838 - airTracks) 5390
        start_time = time.time()

        primary_marks_count = 0
        candidates_count = 0
        tracks_count = 0
        rad_forbidden_count = 0

        print('\r\n\r\n\r\n\r\n        FRAME № %s \r\n' % frame_number)
        data = parse_bin_file(data_structure, frame_size, frame_number)

        for index, group in enumerate(data):
            # ---------------------ЗАПОЛНЯЕМ "BeamTasks"----------------------#
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
                bt_data = read_from('BeamTasks', cur, beam_task,
                                    ['taskId', 'antennaId', 'epsilonBSK', 'betaBSK',
                                     'lowerDistanceTrim', 'upperDistanceTrim', 'lowerVelocityTrim',
                                     'upperVelocityTrim'])
                if bt_data is None:
                    z = prepare_data_for_db('BeamTasks', cur, beam_task)
                    insert_data_to_db('BeamTasks', cur, z)

            # ---------------------ЗАПОЛНЯЕМ "PrimaryMarks"----------------------#
            elif re.search(r'scanData', group[0]):
                group.pop(0)
                scandata = {}
                for c in group:
                    scandata.update(c)

            elif re.search(r'primaryMark', group[0]) and scandata['primaryMarksCount'] != 0:
                group.pop(0)
                primary_marks_count += 1
                primary_mark = {}
                primary_mark.update(scandata)
                for c in group:
                    primary_mark.update(c)

                if primary_marks_count <= scandata['primaryMarksCount']:

                    bt_pk = read_from('BeamTasks', cur, scandata, ['taskId', 'antennaId'])
                    # bt_pk = {k: v for k, v in bt_data.items() if k == 'BeamTask'}
                    primary_mark.update(bt_pk)

                    # Проверка существует ли запись с такими параметрами
                    primary_mark = prepare_data_for_db('PrimaryMarks', cur, primary_mark)
                    pm_data = read_from('PrimaryMarks', cur, primary_mark, ['BeamTask'])
                    if pm_data is None:
                        insert_data_to_db('PrimaryMarks', cur, primary_mark)

            # ---------------------ЗАПОЛНЯЕМ "Candidates"----------------------#
            elif re.search(r'TrackCandidates', group[0]):
                group.pop(0)
                candidate_q = {}
                for c in group:
                    candidate_q.update(c)

            elif re.search(r'trackCandidate', group[0]) and \
                    candidate_q['candidatesQueueSize'] != 0:
                group.pop(0)
                # candidates_count += 1
                track_candidate = {}
                track_candidate.update(candidate_q)
                for c in group:
                    track_candidate.update(c)

            elif re.search(r'viewSpot', group[0]) and \
                    candidate_q['candidatesQueueSize'] != 0:
                group.pop(0)
                view_spot = {}
                # view_spot.update(track_candidate)
                for c in group:
                    view_spot.update(c)

            elif re.search(r'distanceResolutionSpot', group[0]) and \
                    candidate_q['candidatesQueueSize'] != 0:
                group.pop(0)
                distance_res_spot = {}
                for c in group:
                    distance_res_spot.update(c)

            elif re.search(r'velocityResolutionSpot', group[0]) and \
                    candidates_count <= candidate_q['candidatesQueueSize']:
                group.pop(0)
                candidates_count += 1
                velocity_res_spot = {}
                for c in group:
                    # if 'nextUpdateTimeSeconds' in c:
                    velocity_res_spot.update(c)
                # breakpoint()
                # velocity_res_spot.update(view_spot)

                if candidates_count <= candidate_q['candidatesQueueSize']:
                    candidates = {}
                    candidates.update(view_spot)
                    candidate_q['candidatesQueueSize'] -= 1

                    bt_pk = read_from('BeamTasks', cur, candidates, ['taskId', 'antennaId'])
                    candidates.update(bt_pk)

                    candidates = prepare_data_for_db('PrimaryMarks', cur, candidates)
                    pm_pk = read_from('PrimaryMarks', cur, candidates, ['BeamTask', 'azimuth', 'elevation'])

                    if pm_pk:
                        candidates.update(pm_pk)

                        # Проверка существует ли запись с такими параметрами
                        z = prepare_data_for_db('Candidates', cur, candidates)
                        candidate_data = read_from('Candidates', cur, z, ['BeamTask', 'PrimaryMark'])
                        if candidate_data is None:
                            candidates = prepare_data_for_db('Candidates', cur, candidates)
                            insert_data_to_db('Candidates', cur, candidates)

                            # ---------------------ЗАПОЛНЯЕМ "CandidatesIds"----------------------#      2687 frame
                            candidates_ids = {}
                            candidates_ids.update(candidates)
                            candidate_pk = read_from('Candidates', cur, candidates_ids, ['BeamTask', 'PrimaryMark'])

                            candidates_ids.update(candidate_pk)
                            candidates_ids.update(track_candidate)

                            candidates_ids = prepare_data_for_db('CandidatesIds', cur, candidates_ids)
                            insert_data_to_db('CandidatesIds', cur, candidates_ids)

                # ---------------------ЗДЕСЬ------------------------------------------#
                # ---------------------ДОЛЖНА БЫТЬ------------------------------------#
                # ---------------------ВАША РЕКЛАМА-----------------------------------#

            # ---------------------ЗАПОЛНЯЕМ "AirTracks"----------------------#                          2839 frame
            elif re.search(r'\bTracks\b', group[0]):
                tracks_queue = {}
                tracks_queue.update(group[1].items())

            elif re.search(r'track_', group[0]) and tracks_queue['tracksQueuesSize'] != 0:
                tracks_count += 1
                group.pop(0)
                track = {}
                for c in group:
                    track.update(c)

                if track['antennaId'] != 0:

                    pm_data_pk = read_from('PrimaryMarks', cur, track, ['antennaId', 'azimuth', 'elevation'])
                    if pm_data_pk:
                        track.update(pm_data_pk)

                        candidate_data_pk = read_from('Candidates', cur, track,
                                                      ['PrimaryMark', 'BeamTask',
                                                       # 'azimuth', 'elevation'
                                                       ])
                    if pm_data_pk and candidate_data_pk:
                        # pm_data_pk = {k: v for k, v in pm_data.items() if k == 'PrimaryMark'}
                        # candidate_data_pk = {k: v for k, v in candidate_data.items() if k == 'Candidate'}

                        track.update(pm_data_pk)
                        track.update(candidate_data_pk)

                        # Проверка существует ли запись с такими параметрами
                        track_data = read_from('AirTracks', cur, track, ['PrimaryMark', 'Candidate'])
                        if track_data is None:
                            track = prepare_data_for_db('AirTracks', cur, track)
                            insert_data_to_db('AirTracks', cur, track)

            # ---------------------ЗАПОЛНЯЕМ "ForbiddenSectors"----------------------#
            elif re.search(r'\bRadiationForbiddenSectors\b', group[0]):
                group.pop(0)
                rad_forbidden_sector = {}
                for c in group:
                    rad_forbidden_sector.update(c)

            elif re.search(r'RadiationForbiddenSector', group[0]) and \
                    rad_forbidden_sector['RadiationForbiddenSectorsCount'] != 0:
                rad_forbidden_count += 1

                if rad_forbidden_count <= rad_forbidden_sector['RadiationForbiddenSectorsCount']:
                    for c in group:
                        rad_forbidden_sector.update(c)

                    # Проверка существует ли запись с такими параметрами
                    # rad_forbidden_sector = prepare_data_for_db('ForbiddenSectors', cur, rad_forbidden_sector)
                    rad_fs_entity = read_from('ForbiddenSectors', cur, rad_forbidden_sector,
                                              ['azimuthBeginNSSK', 'azimuthEndNSSK',
                                               'elevationBeginNSSK', 'elevationEndNSSK'
                                               ])
                    if rad_fs_entity is None:
                        rad_forbidden_sector = prepare_data_for_db('ForbiddenSectors', cur, rad_forbidden_sector)
                        insert_data_to_db('ForbiddenSectors', cur, rad_forbidden_sector)

        time_sec = "{:7.4f}".format(time.time() - start_time)
        print(f"\r\n----- {time_sec} seconds  -----")
