from ._convertor import to_dict
from ._filter import filter_out_empty


class DataClass:
    def __init__(self, **kwargs):
        self.__set_attributes_from_class()
        self.__set_attributes_from_args(kwargs)

    def __repr__(self) -> str:
        kwargs = [f"{key}={value}" for key, value in self.__dict__.items()]

        return f"{self.__class__.__name__}({', '.join(kwargs)})"

    def to_dict(self, exclude_none: bool = False) -> dict:
        data = to_dict(self)

        return filter_out_empty(data) if exclude_none else data

    def __set_attributes_from_class(self) -> None:
        [
            setattr(self, key, getattr(self, key))
            for key in dir(self.__class__)
            if not key.startswith("__")
            and not key.endswith("__")
            and not callable(getattr(self, key))
        ]

    def __set_attributes_from_args(self, kwargs) -> None:
        for key, value in kwargs.items():
            if key not in self.__dict__.keys():
                raise KeyError(f"{self.__class__} has no key: {key}")

            setattr(self, key, value)
