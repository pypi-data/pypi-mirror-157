from ._get_version_rpc import GetVersion
from ._set_wifi_rpc import SetWifi


class BaseRPCSchema:
    set_wifi = SetWifi
    get_version = GetVersion

    @property
    def __methods__(self):
        return [method for method in dir(self.__class__) if not method.startswith("__")]
