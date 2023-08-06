import time

import ujson

from webduino_core.common.rpc import JSONRPCRequest, JSONRPCResponse, Topic

from ._device_error import HandlerNotFoundError
from .util import Log, MQTTClient

logger = Log(__file__)


class BaseHandler:
    def __init__(self, device_id: str, mqtt_client: MQTTClient):
        self.device_id = device_id
        self.mqtt_client = mqtt_client
        self.__startup_mqtt()

    def __startup_mqtt(self):
        self.mqtt_client.callback = self.__on_message
        self.mqtt_client.connect()
        self.mqtt_client.subscribe(f"{self.device_id}/{Topic.REQUEST}")
        self.mqtt_client.loop()

    def __on_message(self, _: str, message: bytes):
        try:
            self.request = JSONRPCRequest(**ujson.loads(message.decode()))
            handler = getattr(self, f"handle_{self.request.method}")
            payload = JSONRPCResponse(id=self.request.id, result=handler())

            self.response(topic=self.request.response_topic, payload=payload)

        except KeyError as e:
            logger.error(e)
            self.response(
                topic=self.request.response_topic,
                payload=HandlerNotFoundError(id=self.request.id),
            )

    def response(self, topic: str, payload: JSONRPCResponse):
        payload_dict = payload.to_dict(exclude_none=True)

        logger.debug(f"publish >>>")
        logger.debug(f"topic: {self.request.response_topic}")
        logger.debug(f"payload: {payload_dict}")

        self.mqtt_client.publish(
            topic=topic,
            message=ujson.dumps(payload_dict),
        )

    def listen(self):
        while True:
            time.sleep(1)
