from webduino_core.common.rpc import Error, JSONRPCResponse

from ._device_schema import StatusCode


class HandlerNotFoundError(JSONRPCResponse):
    error = Error(code=StatusCode.HANDLER_NOT_FOUND, message="Handler not found")
