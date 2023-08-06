from time import gmtime


class LogLevel:
    ERROR = 0
    WARN = 1
    INFO = 2
    DEBUG = 3


class Log:
    LEVEL: int = LogLevel.DEBUG

    def __init__(self, path: str):
        self._path = path

    def print(self, type: str, message):
        now = "{}-{}-{} {}:{}:{}".format(*gmtime())

        if getattr(LogLevel, type) <= Log.LEVEL:
            print(f"{now} - [{type}] - {self._path} {message}")

    def error(self, message):
        self.print(Log.error.__name__.upper(), message)

    def info(self, message):
        self.print(Log.info.__name__.upper(), message)

    def warn(self, message):
        self.print(Log.warn.__name__.upper(), message)

    def debug(self, message):
        self.print(Log.debug.__name__.upper(), message)
