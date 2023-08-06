from webduino_core.common.rpc import RPC, RPCRequest, RPCResponse


class SetWifiRequest(RPCRequest):
    ssid: str = None
    password: str = None


class SetWifiResponse(RPCResponse):
    is_success: str = None


class SetWifi(RPC):
    request = SetWifiRequest
    response = SetWifiResponse
