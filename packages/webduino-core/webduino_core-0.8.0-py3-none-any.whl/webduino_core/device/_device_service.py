from webduino_core.common.rpc.base import GetVersionResponse, SetWifiResponse

from ._device_handler import BaseHandler


class Device(BaseHandler):

    # TODO: implement
    @property
    def version(self) -> str:
        return "1.0.0"

    # TODO: implement
    def set_wifi(self, ssid: str, password: str) -> dict:
        return True

    def handle_get_version(self) -> GetVersionResponse:
        return GetVersionResponse(version=self.version)

    def handle_set_wifi(self) -> SetWifiResponse:
        return SetWifiResponse(is_success=self.set_wifi(**self.request.params))
