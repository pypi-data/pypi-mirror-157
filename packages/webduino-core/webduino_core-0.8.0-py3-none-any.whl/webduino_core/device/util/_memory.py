import gc


def free(obj):
    try:
        obj.__del__()
    except:
        ...

    obj = None
    del obj
    gc.collect()
