from webduino_core.common.util import DataClass


class RPCRequest(DataClass):
    ...


class RPCResponse(DataClass):
    ...


class RPC:
    request: RPCRequest
    response: RPCResponse
