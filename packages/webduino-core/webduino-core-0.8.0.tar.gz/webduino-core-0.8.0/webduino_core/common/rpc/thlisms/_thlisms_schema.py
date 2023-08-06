from webduino_core.common.rpc.base import BaseRPCSchema

from ._set_config_rpc import SetConfig


class THLISMSRPCSchema(BaseRPCSchema):
    """
    環境感測器 (溫濕度、光度、土壤濕度)
    """

    set_config = SetConfig
