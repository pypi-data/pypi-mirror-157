import _thread
import time

from modules.umqtt.simple import MQTTClient as UMQTTClient


class MQTTClient:
    def __init__(self, client_id: int, hostname: str, port: int, keepalive: int):
        ...

    @property
    def callback(self):
        ...

    @callback.setter
    def callback(self, callback):
        ...

    def connect(self):
        ...

    def publish(self, topic: str, message: str):
        ...

    def subscribe(self, topic: str):
        ...

    def loop(self):
        ...


class MQTTClientAsyncIO(MQTTClient):
    ...


class MQTTClientThread(MQTTClient):
    def __init__(self, client_id: int, hostname: str, port: int, keep_alive: int):
        self._client = UMQTTClient(
            client_id=client_id,
            server=hostname,
            port=port,
            keepalive=keep_alive,
            ssl=False,
        )

    @property
    def callback(self):
        return self._client.cb

    @callback.setter
    def callback(self, callback):
        self._client.set_callback(callback)

    def connect(self):
        self._client.connect()

    def publish(self, topic: str, message: str):
        self._client.publish(topic, message)

    def subscribe(self, topic: str):
        self._client.subscribe(topic)

    def loop(self):
        _thread.start_new_thread(self.__read_message_task, ())

    def __read_message_task(self):
        while True:
            self._client.wait_msg()
            time.sleep(0.01)
