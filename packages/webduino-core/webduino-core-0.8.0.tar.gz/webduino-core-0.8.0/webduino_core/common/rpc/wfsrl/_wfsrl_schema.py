from webduino_core.common.rpc.Base import BaseRPCSchema

from ._set_config_rpc import SetConfig


class WFSRLRPCSchema(BaseRPCSchema):
    """
    流量控制器 (流量計、繼電器)
    """

    set_config = SetConfig
