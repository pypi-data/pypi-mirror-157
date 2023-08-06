import abc
import json
import pickle


class BaseModel(abc.ABC):
    def __repr__(self):
        return "<" + self.__class__.__name__ + " " + " ".join(
            "{}={}".format(k, repr(v)) for k, v in self.__dict__.items()
        ) + ">"

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def to_pickle(self) -> bytes:
        return pickle.dumps(self)

    @classmethod
    def from_json(cls, data: str):
        return cls(**json.loads(data))

    @classmethod
    def from_pickle(cls, data: bytes):
        return pickle.loads(data)
