import abc
import datetime
import json
import pickle
from typing import Optional


def default_formatter(value):
    if isinstance(value, datetime.datetime):
        return value.isoformat()

    return str(value)


class BaseTagModel(abc.ABC):
    def to_json(self) -> str:
        return json.dumps(self.__dict__, default=default_formatter)

    def to_pickle(self) -> bytes:
        return pickle.dumps(self)

    @classmethod
    def from_json(cls, data: str):
        return cls(**json.loads(data))

    @classmethod
    def from_pickle(cls, data: bytes):
        return pickle.loads(data)

    @classmethod
    def from_dict(cls, data: dict):
        data = {k.replace("-", "_"): v for k, v in data.items()}
        return cls(**data)

    @staticmethod
    def _to_timestamp(ts: str) -> Optional[datetime.datetime]:
        if ts is None:
            return

        return datetime.datetime.utcfromtimestamp(int(ts) / 1000)

    @staticmethod
    def _to_bool(value: str) -> Optional[bool]:
        if value is None:
            return

        return bool(int(value))

    @staticmethod
    def _to_int(value: str) -> Optional[int]:
        if value is None:
            return

        return int(value)

    def __repr__(self):
        return "<{} {}>".format(
            self.__class__.__name__, " ".join("{}={}".format(k, repr(v)) for k, v in self.__dict__.items())
        )
