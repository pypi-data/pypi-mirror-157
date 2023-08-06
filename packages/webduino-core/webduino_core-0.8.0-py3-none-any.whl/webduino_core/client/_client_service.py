import json
import uuid

from webduino_core.common.rpc import JSONRPCRequest, JSONRPCResponse, Topic
from webduino_core.common.rpc.base import BaseRPCSchema
from webduino_core.common.util import is_valid_json_rpc

from ._client_error import InvalidJSONRPCError
from .util import MQTTClient, camel_to_kebab, camel_to_snake


class Device:
    def __init__(
        self, device_id: str, mqtt_client: MQTTClient, rpc_schema: BaseRPCSchema
    ):
        self._device_id = device_id
        self._mqtt_client = mqtt_client
        self.__add_rpc_from_schema(schema=rpc_schema)

    async def connect(self):
        await self._mqtt_client.connect()

    def __add_rpc_from_schema(self, schema):
        for method in schema.__methods__:
            rpc_class = getattr(schema, method)
            rpc = self.__generate_rpc(rpc_class)
            setattr(self, method, rpc)

    def __generate_rpc(self, rpc_class):
        async def rpc(**kwargs) -> rpc_class.response:
            id = str(uuid.uuid4())
            method = camel_to_snake(rpc_class.__name__)
            response_topic = f"{self._device_id}/{Topic.RESPONSE}/{camel_to_kebab(rpc_class.__name__)}/{id}"
            request_topic = f"{self._device_id}/{Topic.REQUEST}"
            params = rpc_class.request(**kwargs).to_dict()

            payload = await self.request(
                payload=JSONRPCRequest(
                    response_topic=response_topic,
                    method=method,
                    params=params,
                    id=id,
                ),
                response_topic=response_topic,
                request_topic=request_topic,
            )
            return rpc_class.response(**payload) if payload else None

        return rpc

    async def request(
        self,
        payload: JSONRPCRequest,
        response_topic: str,
        request_topic: str,
        timeout: float = 3,
    ) -> JSONRPCResponse:
        await self._mqtt_client.subscribe(response_topic)
        await self._mqtt_client.publish(
            request_topic, json.dumps(payload.to_dict(exclude_none=True))
        )
        async with self._mqtt_client.unfiltered_messages(timeout=timeout) as messages:
            async for message in messages:
                if not message:
                    return None

                data = json.loads(message.payload.decode())

                if not is_valid_json_rpc(data):
                    raise InvalidJSONRPCError

                response = JSONRPCResponse(**data)

                if response.error:
                    raise Exception(response.error)

                return response.result
