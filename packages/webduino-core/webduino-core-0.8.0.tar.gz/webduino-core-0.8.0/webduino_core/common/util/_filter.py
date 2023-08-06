def filter_out_empty(obj):
    if isinstance(obj, (list, tuple, set)):
        return type(obj)(filter_out_empty(v) for v in obj if filter_out_empty(v))
    if isinstance(obj, dict):
        return {k: filter_out_empty(v) for k, v in obj.items() if filter_out_empty(v)}

    return obj
