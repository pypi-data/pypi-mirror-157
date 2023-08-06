import os


class Env:
    MQTT_HOST = "192.168.1.104"  # 在 micropython 環境使用 'localhost' 會拋錯
    MQTT_PORT = 1883
    MQTT_KEEP_ALIVE = 60

    @classmethod
    def load_env(cls):
        [
            cls.set_env(key, value)
            for key, value in cls.__dict__.items()
            if not key.startswith("__")
            and not key.endswith("__")
            and not callable(value)
        ]

    @classmethod
    def set_env(cls, key, value):
        try:
            os.environ[key] = str(value)
        except AttributeError:
            os.putenv(key, str(value))
