import datetime
import time
import typing

import TwitchPyRC.models.command_variable as command_variable
import TwitchPyRC.twitch_irc as twitch_irc
from TwitchPyRC.twitch_irc import CHANNELS_TYPE


class CommandHandler:
    def __init__(
            self, pattern: typing.List[typing.Union[str, command_variable.Variable]], event: callable, cooldown: float,
            individual_cooldown: bool, help_text: str = None
    ):
        self.pattern = pattern
        self.event = event
        self.cooldown = cooldown
        self.help_text = help_text
        self.last_used = {} if individual_cooldown else 0

    def get_usage(self) -> str:
        message = "Usage: {}".format(self.pattern_to_string())

        if self.help_text is not None:
            message += " - {}".format(self.help_text)

        return message

    def pattern_to_string(self) -> str:
        return " ".join(i if isinstance(i, str) else "[{}]".format(i) for i in self.pattern)

    def is_individual_cooldown(self) -> bool:
        return isinstance(self.last_used, dict)

    @property
    def individual_cooldown(self) -> bool:
        return self.is_individual_cooldown()

    def matches_pattern(self, message: str) -> typing.Union[bool, dict]:
        args = {}

        message = message.split(" ")
        if len(message) > len(self.pattern):
            return False

        for command, template in zip(message, self.pattern):
            if isinstance(template, str):
                if command != template:
                    return False

            else:
                try:
                    args[template.name] = template.data_type(command)
                except Exception:
                    return False

        for template in self.pattern:
            if isinstance(template, str):
                continue

            if template.name not in args:
                if template.has_default_value():
                    args[template.name] = template.default

                else:
                    return False

        return args

    def get_remaining_cooldown(self, username: str) -> float:
        if self.individual_cooldown:
            if username not in self.last_used:
                self.last_used[username] = 0

            return max(self.last_used[username] + self.cooldown - time.time(), 0)

        else:
            return max(self.last_used + self.cooldown - time.time(), 0)

    def reset_cooldown(self, username: str):
        if self.individual_cooldown:
            self.last_used[username] = time.time()

        else:
            self.last_used = time.time()


class CommandBot(twitch_irc.TwitchIRC):
    def __init__(
            self, token: str, channels: CHANNELS_TYPE, nickname: str = "TwitchChatBot",
            server: str = "irc.chat.twitch.tv", port: int = 6667
    ):
        super().__init__(token, channels, nickname, server, port)
        self._command_handlers: typing.List[CommandHandler] = []

        self.username = None
        self.channel = None
        self.tags = None

    def get_command(self, pattern: typing.Union[typing.List[str], str]) -> CommandHandler:
        if isinstance(pattern, str):
            pattern = [pattern]

        for command in self._command_handlers:
            if all(x == y for x, y in zip(pattern, command.pattern)):
                return command

    def command(
            self, command: typing.List[typing.Union[str, command_variable.Variable]], cooldown: float = 0,
            individual_cooldown: bool = True, help_text: str = None
    ):
        def wrap(f):
            self._command_handlers.append(CommandHandler(command, f, cooldown, individual_cooldown, help_text))
            return f

        return wrap

    def on_message(self, message: str, username: str, channel: str, tags: dict):
        self.username = username
        self.channel = channel
        self.tags = tags

        for handler in self._command_handlers:
            args = handler.matches_pattern(message)
            if args is not False:
                time_left = handler.get_remaining_cooldown(username)
                if time_left == 0:
                    handler.reset_cooldown(username)

                else:
                    self.on_command_cooldown(message, time_left, username, channel, tags)
                    return

                handler.event(**args)

                return

        self.on_unknown_command(message, username, channel, tags)

    def on_unknown_command(self, command: str, username: str, channel: str, tags: dict):
        pass

    def on_command_cooldown(self, command: str, time_left: float, username: str, channel: str, tags: dict):
        delta = datetime.timedelta(seconds=time_left)
        delta = str(delta).split(".")[0]

        self.send_message(
            "The command will become available to you again in {}".format(delta), reply_message_id=tags.id
        )
