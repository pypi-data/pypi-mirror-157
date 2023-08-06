try:
    from ._client_service import Device
    from .util import *
except:
    raise ImportError("MicroPython doesn't support client package.")
