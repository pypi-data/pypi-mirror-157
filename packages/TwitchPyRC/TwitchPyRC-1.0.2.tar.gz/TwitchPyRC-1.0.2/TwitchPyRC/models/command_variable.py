import typing


class NoDefault:
    pass


class Variable:
    def __init__(self, name: str, data_type: typing.Union[type, callable] = str, default=NoDefault):
        self.name = name
        self.data_type = data_type
        self.default = default

    def __repr__(self):
        type_hint = "" if self.data_type is str else ":{}".format(self.data_type.__name__)

        if self.default == NoDefault:
            return "{}{}".format(self.name, type_hint)

        else:
            return "{}{}={}".format(self.name, type_hint, self.default)

    def has_default_value(self) -> bool:
        return self.default != NoDefault
