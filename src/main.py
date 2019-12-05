import logging.config
import time
from pathlib import Path

from data_base_methods import DataBase
from read_blocks_from_telemetry import DataBlocksReader
from read_session_structure import read_session_structure
from read_session_telemetry import TelemetryFrameIterator

logging.config.fileConfig('..\\logging.conf')
log = logging.getLogger('simpleExample')

data_folder = Path(r'../data/session_01/')
planner = data_folder / r'Planner'
planner_rsf = data_folder / r'Planner.rsf'
logger = data_folder / r'logger.log'
dsn = 'dbname=Telemetry user=postgres password=123 host=localhost'
frame_number = 0

if __name__ == "__main__":
    structure = read_session_structure(planner)
    telemetry = TelemetryFrameIterator(planner_rsf, structure, frame_number)
    db = DataBase(dsn)
    start_parsing_time = time.time()
    for frame in telemetry:
        start_frame_time = time.time()
        frame_reader = DataBlocksReader(frame)
        primary_marks_count = 1
        candidates_count = 1
        air_track_count = 1
        forbidden_sectors_count = 1
        # ---------------------------------ЗАПОЛНЯЕМ "BeamTasks"--------------------------------------- #
        for beam_task in frame_reader.beam_tasks():
            beam_task_pk = db.get_pk_beam_tasks(beam_task['taskId'], beam_task['antennaId'], beam_task['taskType'])
            if beam_task_pk is None:
                # beam_task = db.map_bin_fields_to_table('BeamTasks', beam_task)
                fields = ['taskId', 'isFake', 'trackId', 'taskType', 'viewDirectionId', 'antennaId', 'pulsePeriod',
                          'threshold', 'lowerVelocityTrim', 'upperVelocityTrim', 'lowerDistanceTrim',
                          'upperDistanceTrim', 'beamAzimuth', 'beamElevation']
                dict_to_insert = {k: v for k, v in beam_task.items() if k in fields}
                db.insert_to_table('BeamTasks', dict_to_insert)
            else:
                log.warning(f'BeamTask : already exists')
        # ---------------------------------ЗАПОЛНЯЕМ "PrimaryMarks"------------------------------------ #
        for prim_mark in frame_reader.primary_marks():
            log.info(f'PrimaryMark_{primary_marks_count}')
            log.info(f'PrimaryMark type = {prim_mark["markType"]}')
            beam_task_pk = db.get_pk_beam_tasks(prim_mark['taskId'], prim_mark['antennaId'], prim_mark['taskType'])
            if beam_task_pk:
                prim_mark.update({'BeamTask': beam_task_pk})
                primary_mark_pk = db.get_pk_primary_marks(prim_mark['BeamTask'])
                if primary_mark_pk is None:
                    # prim_mark = db.map_bin_fields_to_table('PrimaryMarks', prim_mark)
                    fields = ["BeamTask", "primaryMarkId", "scanTime", "antennaId", "beamAzimuth", "beamElevation",
                              "azimuth", "elevation", "markType", "distance", "dopplerSpeed", "signalLevel",
                              "reflectedEnergy"]
                    dict_to_insert = {k: v for k, v in prim_mark.items() if k in fields}
                    db.insert_to_table('PrimaryMarks', dict_to_insert)
                else:
                    log.warning(f'PrimaryMark : already exists')
            primary_marks_count += 1
        # -----------------------ЗАПОЛНЯЕМ "Candidates" & "CandidatesHistory"-------------------------- #
        for candidate in frame_reader.candidates():
            log.info(f'Candidate_{candidates_count}')
            log.info(f'Candidate state = {candidate["state"]}')
            if candidate['state'] == 1:
                beam_task_pk = db.get_pk_b_tasks_candidates(candidate['id'], candidate['taskId'],
                                                            candidate['antennaId'], 1)
            else:
                beam_task_pk = db.get_pk_b_tasks_candidates(candidate['id'], candidate['taskId'],
                                                            candidate['antennaId'], 2)

            if beam_task_pk:
                candidate.update({'BeamTask': beam_task_pk})
                pm_pk = db.get_pk_primary_marks(candidate['BeamTask'])
                if pm_pk:
                    candidate.update({'PrimaryMark': pm_pk})
                    candidates_pk = db.get_pk_candidates(candidate['id'])
                    # if dict_for_get_pk['id'] != 0:
                    if candidates_pk is None:
                        # cand = db.map_bin_fields_to_table('Candidates', candidate)
                        fields = ['id']
                        dict_to_insert = {k: v for k, v in candidate.items() if k in fields}
                        db.insert_to_table('Candidates', dict_to_insert)
                        candidates_pk = db.get_pk_candidates(candidate['id'])
                    else:
                        log.warning(f'Candidate : already exists')
                    candidate.update({'Candidate': candidates_pk})
                    candidates_history_pk = db.get_pk_cand_hists(candidate['BeamTask'], candidate['PrimaryMark'])
                    if candidates_history_pk is None:
                        # candidate = db.map_bin_fields_to_table('CandidatesHistory', candidate)
                        fields = ["BeamTask", "PrimaryMark", "Candidate", "azimuth", "elevation", "state",
                                  "distanceZoneWidth", "velocityZoneWidth", "numDistanceZone", "numVelocityZone",
                                  "antennaId", "timeUpdated"]
                        dict_to_insert = {k: v for k, v in candidate.items() if k in fields}
                        db.insert_to_table('CandidatesHistory', dict_to_insert)
                    else:
                        log.warning(f'CandidateHistory : already exists')
            candidates_count += 1
        # ------------------------ЗАПОЛНЯЕМ "AirTracks" & "AirTracksHistory"--------------------------- #
        for air_track in frame_reader.air_tracks():
            log.info(f'AirTrack_{air_track_count}')
            log.info(f'AirTrack type = {air_track["type"]}')
            air_marks_misses = frame_reader.air_marks_misses()
            beam_task_pk = db.get_pk_b_tasks_air_tracks(air_track['id'], air_track['antennaId'], 3)
            if beam_task_pk:
                air_track.update({'BeamTask': beam_task_pk})
                pm_pk = db.get_pk_primary_marks(air_track['BeamTask'])
                if pm_pk:
                    air_track.update({'PrimaryMark': pm_pk})
                    candidates_history_pk = db.get_pk_cand_hists(air_track['BeamTask'], air_track['PrimaryMark'])
                    if candidates_history_pk:
                        air_track.update({'CandidatesHistory': candidates_history_pk})
                        air_track_pk = db.get_pk_air_tracks(air_track['id'])
                        if air_track_pk is None:
                            # airs = db.map_bin_fields_to_table('AirTracks', air_track)
                            fields = ['id']
                            dict_to_insert = {k: v for k, v in air_track.items() if k in fields}
                            db.insert_to_table('AirTracks', dict_to_insert)
                            air_track_pk = db.get_pk_air_tracks(air_track['id'])
                        else:
                            log.warning(f'AirTrack : already exists')
                        air_track.update({'AirTrack': air_track_pk})
                        air_track_history_pk = db.get_pk_tracks_hists(air_track['PrimaryMark'],
                                                                      air_track['CandidatesHistory'])
                        if air_track_history_pk is None:
                            # air_track = db.map_bin_fields_to_table('AirTracksHistory', air_track)
                            fields = ["PrimaryMark", "CandidatesHistory", "AirTrack", "type", "priority",
                                      "antennaId", "azimuth", "elevation", "distance", "radialVelocity",
                                      "pulsePeriod", "missesCount", "possiblePeriods", "nextTimeUpdate",
                                      "scanPeriod", "sigmaAzimuth", "sigmaElevation", "sigmaDistance",
                                      "sigmaRadialVelocity", "minDistance", "maxDistance", "minRadialVelocity",
                                      "maxRadialVelocity"]
                            dict_to_insert = {k: v for k, v in air_track.items() if k in fields}
                            db.insert_to_table('AirTracksHistory', dict_to_insert)
                        else:
                            log.warning(f'AirTracksHistory : already exists')
            air_track_count += 1
        # ------------------------------ЗАПОЛНЯЕМ "ForbiddenSectors"----------------------------------- #
        for forbidden_sector in frame_reader.forbidden_sectors():
            log.info(f'forbiddenSector_{forbidden_sectors_count}')
            fs_pk = db.get_pk_forb_sectors(forbidden_sector['azimuth_b_nssk'], forbidden_sector['azimuth_e_nssk'],
                                           forbidden_sector['elevation_b_nssk'], forbidden_sector['elevation_e_nssk'])
            if fs_pk is None:
                # forbidden_sector = db.map_bin_fields_to_table('ForbiddenSectors', forbidden_sector)
                fields = ["azimuth_b_nssk", "azimuth_e_nssk", "elevation_b_nssk", "elevation_e_nssk"]
                dict_to_insert = {k: v for k, v in forbidden_sector.items() if k in fields}
                db.insert_to_table('ForbiddenSectors', dict_to_insert)
            else:
                log.warning(f'ForbiddenSector : already exists')
            forbidden_sectors_count += 1
        # - FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN -- FIN --- #
        time_sec = "{:3.4f}".format(time.time() - start_frame_time)
        log.info(f"------------------------- {time_sec} seconds -------------------------\r\n\r\n")

    minutes = "{:3.2f}".format(float(time.time() - start_parsing_time) / 60)
    log.info(f"------------------------- {minutes} minutes -------------------------\r\n\r\n")
