from text_file_parser import *
from bin_file_parser import *
from data_base_methods import *
import time

if __name__ == "__main__":
    # Парсим текстовый файл
    data_structure, frame_size = parse_text_file()
    # Вычисляем количество кадров
    frame_c = frame_counter(frame_size)
    # Соединяемся с БД
    cur, conn = connection()
    # Парсим бинарник по кадрам
    # frame_number = 300 - Candidates; 2237 2838 - airTracks
    for frame_number in range(4282, frame_c):
        start_time = time.time()
        print('\r\n\r\n\r\n\r\n       FRAME № %s \r\n' % frame_number)
        data = parse_bin_file(data_structure, frame_size, frame_number)

        primary_marks_count = 0
        candidates_count = 0
        tracks_count = 0
        rad_forbidden_count = 0

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
                bt_data = read_from('BeamTasks', cur, beam_task, ['taskId', 'antennaId'])
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

                    bt_data = read_from('BeamTasks', cur, scandata, ['taskId', 'antennaId'])
                    bt_pk = {k: v for k, v in bt_data.items() if k == 'BeamTask'}
                    primary_mark.update(bt_pk)

                    # Проверка существует ли запись с такими параметрами
                    pm_data = read_from('PrimaryMarks', cur, primary_mark, ['BeamTask'])
                    if pm_data is None:
                        primary_mark = prepare_data_for_db('PrimaryMarks', cur, primary_mark)
                        insert_data_to_db('PrimaryMarks', cur, primary_mark)

            # ---------------------ЗАПОЛНЯЕМ "Candidates"----------------------#
            elif re.search(r'TrackCandidates', group[0]):
                group.pop(0)
                candidate_q = {}
                for c in group:
                    candidate_q.update(c)

            elif re.search(r'trackCandidate', group[0]) and \
                    candidate_q['candidatesQueueSize'] != 0:
                candidates_count += 1
                group.pop(0)
                track_candidate = {}
                track_candidate.update(candidate_q)
                for c in group:
                    track_candidate.update(c)

            elif re.search(r'viewSpot', group[0]) and \
                    candidate_q['candidatesQueueSize'] != 0:
                group.pop(0)
                view_spot = {}
                view_spot.update(track_candidate)
                for c in group:
                    view_spot.update(c)

            elif re.search(r'velocityResolutionSpot', group[0]) and \
                    candidate_q['candidatesQueueSize'] != 0:
                group.pop(0)
                velocity_res_spot = {}
                velocity_res_spot.update(view_spot)
                for c in group:
                    if 'nextUpdateTimeSeconds' in c:
                        velocity_res_spot.update(c)

                if candidates_count <= candidate_q['candidatesQueueSize']:

                    bt_data = read_from('BeamTasks', cur, velocity_res_spot, ['taskId', 'antennaId'])
                    bt_pk = {k: v for k, v in bt_data.items() if k == 'BeamTask'}

                    pm_data = read_from('PrimaryMarks', cur, velocity_res_spot, ['azimuth', 'elevation'])
                    if pm_data:
                        pm_pk = {k: v for k, v in pm_data.items() if k == 'PrimaryMark'}

                        velocity_res_spot.update(bt_pk)
                        velocity_res_spot.update(pm_pk)

                        z = {}
                        z.update(bt_pk)
                        z.update(pm_pk)
                        candidate_data = read_from_db('Candidates', cur, z)

                        if candidate_data is None:
                            candidates = prepare_data_for_db('Candidates', cur, velocity_res_spot)
                            insert_data_to_db('Candidates', cur, candidates)

                            # ---------------------ЗАПОЛНЯЕМ "CandidatesIds"----------------------#
                            candidates_ids = {}
                            candidate_data = read_from_db(
                                'Candidates', cur, {k: velocity_res_spot[k] for k in ('BeamTask', 'PrimaryMark')})

                            candidate_data_pk = {k: v for k, v in candidate_data.items() if k == 'Candidate'}
                            candidates_ids.update(velocity_res_spot)
                            candidates_ids.update(candidate_data_pk)

                            candidates_ids = prepare_data_for_db('CandidatesIds', cur, candidates_ids)
                            insert_data_to_db('CandidatesIds', cur, candidates_ids)

                # ---------------------ЗДЕСЬ------------------------------------------#
                # ---------------------ДОЛЖНА БЫТЬ------------------------------------#
                # ---------------------ВАША РЕКЛАМА-----------------------------------#

            # ---------------------ЗАПОЛНЯЕМ "AirTracks"----------------------#
            elif re.search(r'\bTracks\b', group[0]):
                tracks_queue = {}
                tracks_queue.update(group[1].items())

            elif re.search(r'track_', group[0]) and tracks_queue['tracksQueuesSize'] != 0:
                tracks_count += 1
                group.pop(0)
                track = {}
                for c in group:
                    track.update(c)

                pm_data = read_from('PrimaryMarks', cur, track, ['antennaId'])
                candidate_data = read_from('Candidates', cur, track, ['azimuth', 'elevation'])
                if pm_data and candidate_data:
                    pm_data_pk = {k: v for k, v in pm_data.items() if k == 'PrimaryMark'}
                    candidate_data_pk = {k: v for k, v in candidate_data.items() if k == 'Candidate'}

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
