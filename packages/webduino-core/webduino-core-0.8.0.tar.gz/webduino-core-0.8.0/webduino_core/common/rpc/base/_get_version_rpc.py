from webduino_core.common.rpc import RPC, RPCRequest, RPCResponse


class GetVersionRequest(RPCRequest):
    ...


class GetVersionResponse(RPCResponse):
    version: str = None


class GetVersion(RPC):
    request = GetVersionRequest
    response = GetVersionResponse
