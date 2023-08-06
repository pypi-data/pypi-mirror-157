from webduino_core.common.rpc import RPC, RPCRequest, RPCResponse


# TODO: implement
class SetConfigRequest(RPCRequest):
    ...


class SetConfigResponse(RPCResponse):
    is_success: str = None


class SetConfig(RPC):
    request = SetConfigRequest
    response = SetConfigResponse
