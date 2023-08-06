import typing


class NoDefault:
    pass


class Variable:
    def __init__(self, name: str, data_type: typing.Union[type, callable] = str, default=NoDefault):
        self.name = name
        self.data_type = data_type
        self.default = default

    def __repr__(self):
        data_type = self.data_type.__name__
        if self.default == NoDefault:
            return "{}: {}".format(self.name, data_type)

        else:
            return "{}: {} = {}".format(self.name, data_type, self.default)

    def has_default_value(self) -> bool:
        return self.default != NoDefault
