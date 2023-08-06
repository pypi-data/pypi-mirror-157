from webduino_core.common.util import DataClass


class Topic:
    REQUEST = "request"
    RESPONSE = "response"


class Error(DataClass):
    code: int = None
    message: str = None
    data: str = None


class JSONRPCRequest(DataClass):
    jsonrpc: str = "2.0"
    response_topic: str = None
    method: str = None
    params: dict = None
    id: str = None


class JSONRPCResponse(DataClass):
    jsonrpc: str = "2.0"
    result = None
    error: Error = None
    id: str = None
