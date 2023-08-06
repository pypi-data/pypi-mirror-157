import sys

sys.path.append("../..")

import os

from webduino_core.device import Device
from webduino_core.device.util import MQTTClientThread
from webduino_core.env import Env

Env.load_env()

if __name__ == "__main__":
    device_id = "device-id"
    device = Device(
        device_id=device_id,
        mqtt_client=MQTTClientThread(
            client_id=device_id,
            hostname=os.getenv("MQTT_HOST"),
            port=int(os.getenv("MQTT_PORT")),
            keep_alive=int(os.getenv("MQTT_KEEP_ALIVE")),
        ),
    )

    device.listen()
