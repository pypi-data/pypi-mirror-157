import sys

sys.path.append("../..")

import asyncio
import os

from webduino_core.client import Device, MQTTClient
from webduino_core.common.rpc.thlisms import THLISMSRPCSchema
from webduino_core.env import Env

Env.load_env()


async def main():
    device = Device(
        device_id="device-id",
        mqtt_client=MQTTClient(
            hostname=os.getenv("MQTT_HOST"),
            port=int(os.getenv("MQTT_PORT")),
            keepalive=int(os.getenv("MQTT_KEEP_ALIVE")),
        ),
        rpc_schema=THLISMSRPCSchema(),
    )
    await device.connect()

    result = await device.get_version()
    print(f"Version: {result.version}")

    result = await device.set_wifi(ssid="ssid", password="password")
    print(f"Set WiFi Result: {result.is_success}")


asyncio.run(main())
