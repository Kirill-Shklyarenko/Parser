import inspect


def mapper(func):
    def wrapper_decorator(*args, **kwargs):
        map_fields = {}
        func_name = func.__name__
        if func_name == 'beam_tasks':
            map_fields = {'beamAzimuth': 'betaBSK', 'beamElevation': 'epsilonBSK'}
        elif func_name == 'primary_marks':
            map_fields = {'primaryMarkId': 'id', 'markType': 'type', 'scanTime': 'processingTime'}
        elif func_name == 'candidates':
            map_fields = {'timeUpdated': 'creationTimeSeconds'}
        elif func_name == 'air_tracks':
            map_fields = {'timeUpdated': 'nextUpdateTimeSeconds', 'scanPeriod': 'scanPeriodSeconds', }
        elif func_name == 'forbidden_sectors':
            map_fields = {'azimuthBeginNSSK': 'minAzimuth', 'azimuthEndNSSK': 'maxAzimuth',
                          'elevationBeginNSSK': 'minElevation', 'elevationEndNSSK': 'maxElevation', }
        value = func(*args, **kwargs)

        for dicts in value:
            for fk, fv in dicts.items():
                for sk, sv in map_fields.items():
                    if fk == sv:
                        dicts.update({sk: fv})
                        del dicts[fk]
        return value

    return wrapper_decorator


def pk(func):
    def wrapper_decorator(*args, **kwargs):
        data = {}
        fields_for_get_pk = {}
        if args[1] == 'BeamTasks' and args[2] == 'BeamTask':
            get_pk_bt = {'taskId': 'taskId', 'antennaId': 'antennaId'}
            fields_for_get_pk = get_pk_bt
        if args[1] == 'PrimaryMarks' and args[2] == 'PrimaryMark':
            get_pk_pm = {'BeamTask': 'BeamTask'}
            fields_for_get_pk = get_pk_pm
        if args[1] == 'Candidates' and args[2] == 'Candidate':
            get_pk_candidate = {'id': 'id'}
            fields_for_get_pk = get_pk_candidate
        if args[1] == 'CandidatesHistory' and args[2] == 'CandidateHistory':
            get_pk_candidate_hist = {'BeamTask': 'BeamTask', 'PrimaryMark': 'PrimaryMark'}
            fields_for_get_pk = get_pk_candidate_hist

        for fk, fv in args[3].items():
            for sk, sv in fields_for_get_pk.items():
                if fk == sv:
                    data.update({sk: fv})

        if 'data' not in inspect.getfullargspec(func).args:
            kwargs['data'] = data
        func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper_decorator
