from text_file_parser import *
from bin_file_parser import *
from data_base_methods import *
import re


if __name__ == "__main__":
    # Парсим текстовый файл
    data_structure, frame_size = parse_text_file()
    # Вычисляем количество кадров
    frame_c = frame_counter(frame_size)
    # Соединяемся с БД
    cur, conn = connection()
    # Парсим бинарник по кадрам
    # frame_number = 1947
    for frame_number in range(1063, frame_c):
        print('\r\nFRAME № %s \r\n' % frame_number)
        data = parse_bin_file(data_structure, frame_size, frame_number)

        primary_marks_count = 0
        candidates_count = 0
        tracks_count = 0
        rad_forbidden_count = 0

        for index, group in enumerate(data):
            # ---------------------ЗАПОЛНЯЕМ "BeamTasks"----------------------#
            if re.search(r'\bTask\b', group[0]):
                task_task_id = {}
                task_task_id.update(group[1].items())
            elif re.search(r'beamTask', group[0]):
                group.pop(0)
                group.append(task_task_id)
                z = prepare_data_for_db('BeamTasks', cur, group)
                group.clear()
                insert_data_to_db('BeamTasks', cur, z)

            # ---------------------ЗАПОЛНЯЕМ "PrimaryMarks"----------------------#
            elif re.search(r'scanData', group[0]):
                group.pop(0)
                scandata = {}
                for c in group:
                    scandata.update(c)
                group.clear()

            elif re.search(r'primaryMark', group[0]) and scandata['primaryMarksCount'] != 0:
                primary_marks_count += 1
                group.pop(0)
                if primary_marks_count <= scandata['primaryMarksCount']:
                    read_data = read_data_from_db('BeamTasks', cur,
                                                  {k: scandata[k] for k in ('taskId', 'antennaId', 'taskType')})
                    group.append({k: v for k, v in read_data.items() if k == 'BeamTask'})
                    for k in [{k: v} for k, v in scandata.items()]:
                        group.append(k)
                    z = prepare_data_for_db('PrimaryMarks', cur, group)
                    group.clear()
                    insert_data_to_db('PrimaryMarks', cur, z)

            # ---------------------ЗАПОЛНЯЕМ "Candidates"----------------------#
            elif re.search(r'TrackCandidates', group[0]):
                candidate_queue = {}
                candidate_queue.update(group[1].items())
                group.pop(0)

            elif re.search(r'trackCandidate', group[0]) and \
                    candidate_queue['candidatesQueueSize'] != 0:
                candidates_count += 1
                group.pop(0)
                track_candidate = {}
                for c in group:
                    track_candidate.update(c)
                group.clear()

            elif re.search(r'viewSpot', group[0]) and \
                    candidate_queue['candidatesQueueSize'] != 0:
                group.pop(0)
                view_spot = {}
                for c in group:
                    if 'distancePeriod' in c:
                        view_spot.update(c)
                    elif 'velocityPeriod' in c:
                        view_spot.update(c)
                    elif 'distance' in c:
                        view_spot.update(c)
                    elif 'velocity' in c:
                        view_spot.update(c)
                group.clear()

            elif re.search(r'velocityResolutionSpot', group[0]) and \
                    candidate_queue['candidatesQueueSize'] != 0:
                group.pop(0)
                velocity_res_spot = {}
                for c in group:
                    if 'nextUpdateTimeSeconds' in c:
                        velocity_res_spot.update(c)

                if candidates_count <= candidate_queue['candidatesQueueSize']:
                    candidate = {}
                    candidate.update(track_candidate)
                    candidate.update(view_spot)
                    candidate.update(velocity_res_spot)

                    bt_data = read_data_from_db('BeamTasks', cur, {k: candidate[k] for k in ('taskId', 'antennaId')})
                    beam_task_pk = {k: v for k, v in bt_data.items() if k == 'BeamTask'}

                    cand_keys = {k: candidate[k] for k in ('azimuth', 'elevation', 'beamAzimuth', 'beamElevation')}
                    z = {}
                    z.update(beam_task_pk)
                    z.update(cand_keys)
                    pm_data = read_data_from_db('PrimaryMarks', cur, z)

                    if bt_data and pm_data:
                        primary_mark_pk = {k: v for k, v in pm_data.items() if k == 'PrimaryMark'}
                        candidate.update(beam_task_pk)
                        candidate.update(primary_mark_pk)
                        z = prepare_data_for_db('Candidates', cur, [{k: v} for k, v in candidate.items()])
                        group.clear()
                        insert_data_to_db('Candidates', cur, z)

                # ---------------------ЗАПОЛНЯЕМ "CandidatesIds"----------------------#
                candidate_ids = {}
                zapros = [
                    'PrimaryMark',
                    'BeamTask',
                    # 'azimuth',
                    # 'elevation'
                ]
                # формирование строки запроса
                columns = ','.join([f'"{x}"' for x in zapros])
                # param_placeholders = ','.join(['%s' for x in range(len(data))])
                query = f'SELECT DISTINCT ({columns}) FROM "Candidates"'
                # param_values = tuple(x for x in data.values())
                # param_values = (3, 1)
                # try:
                #     cur.execute(query)
                # except Exception as e:
                #     print(f'\r\nException: {e}')
                # else:
                #     db_values = cur.fetchall()
                #     if db_values:
                #         for c, i in enumerate(db_values):
                #             print(zapros)
                #             print(db_values[c])
                # ---------------------ЗДЕСЬ------------------------------------------#
                # ---------------------ДОЛЖНА БЫТЬ------------------------------------#
                # ---------------------ВАША РЕКЛАМА-----------------------------------#

            # ---------------------ЗАПОЛНЯЕМ "AirTracks"----------------------#
            elif re.search(r'\bTracks\b', group[0]):
                tracks_queue = {}
                tracks_queue.update(group[1].items())
                group.pop(0)

                # tracks_queue['tracksQueuesSize'] = 4

                # if tracks_queue['tracksQueuesSize'] != 0:
                # breakpoint()

            elif re.search(r'track_', group[0]) and tracks_queue['tracksQueuesSize'] != 0:
                tracks_count += 1
                group.pop(0)
                track = {}
                for c in group:
                    track.update(c)
                group.clear()

                if track['antennaId'] != 0:
                    breakpoint()

                pm_data = read_data_from_db('PrimaryMarks', cur, {k: v for k, v in track.items() if k == 'antennaId'})
                candidate_data = read_data_from_db('Candidates', cur, {k: track[k] for k in ('azimuth',
                                                                                             'elevation')})
                if pm_data and candidate_data:
                    pm_data_pk = {k: v for k, v in pm_data.items() if k == 'PrimaryMark'}
                    candidate_data_pk = {k: v for k, v in candidate_data.items() if k == 'Candidate'}

                    track.update(pm_data_pk)
                    track.update(candidate_data_pk)
                    z = prepare_data_for_db('AirTracks', cur, track)
                    group.clear()
                    insert_data_to_db('AirTracks', cur, z)

            # ---------------------ЗАПОЛНЯЕМ "ForbiddenSectors"----------------------#
            elif re.search(r'\bRadiationForbiddenSectors\b', group[0]):
                group.pop(0)
                rad_forbidden_sector = {}
                for c in group:
                    rad_forbidden_sector.update(c)
                group.clear()

                if rad_forbidden_sector['RadiationForbiddenSectorsCount'] != 0:
                    breakpoint()

            elif re.search(r'RadiationForbiddenSector', group[0]) and\
                    rad_forbidden_sector['RadiationForbiddenSectorsCount'] != 0:
                rad_forbidden_count += 1
                group.pop(0)
                if rad_forbidden_count <= rad_forbidden_sector['RadiationForbiddenSectorsCount']:
                    for c in group:
                        rad_forbidden_sector.update(c)

                    z = prepare_data_for_db('ForbiddenSectors', cur, rad_forbidden_sector)
                    group.clear()
                    breakpoint()
                    insert_data_to_db('ForbiddenSectors', cur, z)
