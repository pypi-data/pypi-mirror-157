import typing

import TwitchPyRC.models.base_model as base_model


class Message(base_model.BaseModel):
    def __init__(self, tags, nickname, host, command, args):
        self.tags: dict = tags
        self.nickname: str = nickname
        self.host: str = host
        self.command: list = command
        self.args: str = args

    @property
    def raw_command(self) -> str:
        return self.command[0]

    @property
    def channel(self) -> typing.Union[str, None]:
        try:
            return self.command[1]
        except IndexError:
            return

    def get_command(self) -> str:
        return self.command[0]

    def to_small_string(self):
        return "<Message command={} channel={} nickname={} args={}>".format(
            repr(self.raw_command), repr(self.channel), repr(self.nickname), repr(self.args)
        )
