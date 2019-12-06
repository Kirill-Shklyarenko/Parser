def converter(map_fields):
    def mapper(func):
        def wrapper_decorator(frame: list):
            container = func(frame)
            for dicts in container:
                for k1, v1 in dicts.items():
                    for k2, v2 in map_fields.items():
                        if k1 == v2:
                            dicts.update({k2: v1})
                            del dicts[k1]
            return container

        return wrapper_decorator

    return mapper
