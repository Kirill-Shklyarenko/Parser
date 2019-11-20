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

        if args[1] == 'BeamTasks' and args[2] == 'BeamTask':
            get_pk_bt = {'taskId': 'taskId', 'antennaId': 'antennaId'}

        for fk, fv in args[3].items():
            for sk, sv in get_pk_bt.items():
                if fk == sv:
                    data.update({sk: fv})

        if 'data' not in inspect.getfullargspec(func).args:
            kwargs['data'] = data
        func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper_decorator
