import json
import pathlib
import socket
import threading
import time
import typing
import logging
import TwitchPyRC.models.message_model as message_model
import TwitchPyRC.models.tag_models.clear_chat as clear_chat_model
import TwitchPyRC.models.tag_models.message_sent as message_sent_model
import TwitchPyRC.models.tag_models.clear_message as clear_message_model
import TwitchPyRC.models.tag_models.whisper as whisper_model
import TwitchPyRC.parsers as parsers

CHANNELS_TYPE = typing.Union[typing.List[str], str]
RECONNECTION_DELAY = 2


class TwitchIRC:
    LOG_HANDLE = "TwitchPyRC"

    def __init__(
            self, token: str, channels: CHANNELS_TYPE, nickname: str = "TwitchChatBot",
            server: str = "irc.chat.twitch.tv", port: int = 6667
    ):
        """
        A bot to interact with Twitch Chat
        :param token: Obtain from https://twitchapps.com/tmi/
        :param channels:
        :param nickname:
        :param server:
        :param port:
        """
        self._token = token
        self._channels = self._get_channels(channels)
        self._nickname = nickname
        self._server = server
        self._port = port

        self.logger = logging.getLogger(self.LOG_HANDLE)
        self.logger.setLevel(logging.INFO)

        self._session_channel = None

        self._sock: socket.socket = None

        if not self._token.startswith("oauth:"):
            self._token = "oauth:{}".format(self._token)

        self.reconnect()

    @classmethod
    def from_dict(cls, data: dict):
        if "token" not in data:
            raise ValueError(
                "'token' must be specified to instantiate. You can obtain a token from https://twitchapps.com/tmi/"
            )

        if "channels" not in data:
            raise ValueError(
                "'channels' must be specified to instantiate. "
                "You must specify which channel or channels you wish to connect to"
            )

        return cls(
            token=data["token"],
            channels=data["channels"],
            nickname=data.get("nickname", "TwitchChatBot"),
            server=data.get("server", "irc.chat.twitch.tv"),
            port=data.get("port", 6667),
        )

    @classmethod
    def from_json(cls, data: str):
        return cls.from_dict(json.loads(data))

    @classmethod
    def from_file(cls, path: typing.Union[str, pathlib.Path]):
        with open(path) as file_buffer:
            return cls.from_json(file_buffer.read())

    @staticmethod
    def create_credentials_template(path: typing.Union[str, pathlib.Path]):
        with open(path, 'w') as file_buffer:
            file_buffer.write(json.dumps(dict(
                token="oauth:xxxxx",
                channels="cpsuperstore"
            ), sort_keys=True, indent=4, default=str))

    def _get_channels(self, channels: CHANNELS_TYPE = None) -> list:
        if channels is None:
            return self._channels if self._session_channel is None else [
                "#{}".format(self._session_channel.lower().lstrip("#"))
            ]

        if isinstance(channels, (list, tuple, set)):
            for i, channel in enumerate(channels):
                if not channel.startswith("#"):
                    channels[i] = "#{}".format(channel.lower())
                else:
                    channels[i] = channel.lower()

            return channels

        if not channels.startswith("#"):
            channels = "#{}".format(channels.lower())

        return [channels]

    def _execute_message(self, message: message_model.Message):
        mode = self.logger.info

        if message.raw_command == "PRIVMSG":
            self.on_message(
                message.args, message.nickname, message.channel, message_sent_model.MessageSent.from_dict(message.tags)
            )

        elif message.raw_command == "CLEARCHAT":
            self.on_clear_chat(message.channel, clear_chat_model.ClearChat.from_dict(message.tags), message.args)

        elif message.raw_command == "CLEARMSG":
            self.on_clear_message(
                message.args, message.channel, clear_message_model.ClearMessage.from_dict(message.tags)
            )

        elif message.raw_command == "HOSTTARGET":
            args = message.args.split(" ")
            if args[0] == "-":
                self.on_host_end(int(args[1]), message.channel)
            else:
                self.on_host_start(args[0], int(args[1]), message.channel)

        elif message.raw_command == "JOIN":
            self.on_user_join(message.nickname, message.channel)

        elif message.raw_command == "PART":
            self.on_user_leave(message.nickname, message.channel)

        elif message.raw_command == "WHISPER":
            self.on_whisper(message.args, message.nickname, whisper_model.Whisper.from_dict(message.tags))

        elif message.raw_command == "USERNOTICE":
            self.on_user_notice(message.channel, message.tags, message.args)

        else:
            mode = self.logger.debug

        mode("Received {}".format(message.to_small_string()))

    def reconnect(self):
        if self._sock is not None:
            self.logger.info("Closing old IRC connection...")
            self._sock.close()

        self.logger.info("Establishing new connection to IRC server at {}:{}".format(self._server, self._port))
        self._sock = socket.socket()

        self._sock.connect((self._server, self._port))

        self.logger.info("Joining channels {} with nickname {}".format(
            ", ".join(self._channels).replace("#", ""), self._nickname)
        )

        self._sock.send("PASS {}\n".format(self._token).encode('utf-8'))
        self._sock.send("NICK {}\n".format(self._nickname).encode('utf-8'))
        self._sock.send("JOIN {}\n".format(",".join(self._channels)).encode('utf-8'))
        self._sock.send("CAP REQ :twitch.tv/commands twitch.tv/membership twitch.tv/tags\n".encode('utf-8'))

        self.logger.info("Successfully connected to IRC server")

    def start(self):
        while True:
            try:
                resp = self._sock.recv(2048).decode('utf-8')
            except ConnectionResetError:
                self.logger.warning(
                    "An existing connection was forcibly closed by the remote host... "
                    "Attempting reconnection in {} seconds".format(RECONNECTION_DELAY)
                )
                time.sleep(RECONNECTION_DELAY)
                self.reconnect()
                continue

            resp = resp.replace("\r", "")

            resp = resp.replace("\r\n", "\n").rstrip("\n")
            for message in resp.split("\n"):

                if message.startswith('PING'):

                    self._sock.send("PONG\n".encode('utf-8'))

                elif len(message) > 0:
                    self.logger.debug("Received {}".format(message))
                    parsed_message = parsers.parse_message(message)

                    self._session_channel = parsed_message.channel
                    self._execute_message(parsed_message)
                    self._session_channel = None

    def start_sync(self):
        self.start()

    def start_async(self, thread_name: str = "TwitchChatBot", daemon: bool = True) -> threading.Thread:
        self.logger.info("Spawning {}thread named {} for asynchronous IRC communication".format(
            "daemon " if daemon else "", thread_name
        ))
        thread = threading.Thread(target=self.start, name=thread_name, daemon=daemon)
        thread.start()
        return thread

    def send_message(self, message: str, channel: CHANNELS_TYPE = None, reply_message_id: str = None):
        prefix = ""
        if reply_message_id is not None:
            prefix = "@reply-parent-msg-id={} ".format(reply_message_id)

        channels = self._get_channels(channel)

        self.logger.info("Sending message {} to channel(s) {}".format(
            message, ", ".join(channels).replace("#", "")
        ))

        for c in channels:
            self._sock.send((prefix + "PRIVMSG {} :{}\r\n".format(c, message)).encode("utf-8"))

    def command_ban(self, username: str, reason: str = "", channel: CHANNELS_TYPE = None):
        self.send_message("/ban {} {}".format(username, reason), channel)

    def command_unban(self, username: str, channel: CHANNELS_TYPE = None):
        self.send_message("/unban {}".format(username), channel)

    def command_clear(self, channel: CHANNELS_TYPE = None):
        self.send_message("/clear", channel)

    def command_color(self, color: str, channel: CHANNELS_TYPE = None):
        self.send_message("/color {}".format(color), channel)

    def command_commercial(self, length: int = 30, channel: CHANNELS_TYPE = None):
        if length not in (30, 60, 90, 120, 150, 180):
            raise ValueError("Provided length {} is not valid. Please choose from 30, 60, 90, 120, 150, 180!".format(
                length
            ))

        self.send_message("/commercial {}".format(length), channel)

    def command_delete(self, message_id: str, channel: CHANNELS_TYPE = None):
        self.send_message("/delete {}".format(message_id), channel)

    def command_disconnect(self, channel: CHANNELS_TYPE = None):
        self.send_message("/disconnect", channel)

    def command_emote_only(self, channel: CHANNELS_TYPE = None):
        self.send_message("/emoteonly", channel)

    def command_emote_only_on(self, channel: CHANNELS_TYPE = None):
        self.command_emote_only(channel)

    def command_emote_only_off(self, channel: CHANNELS_TYPE = None):
        self.send_message("/emoteonlyoff", channel)

    def command_followers_only(self, length: int = 1, channel: CHANNELS_TYPE = None):
        self.send_message("/followers {}".format(length), channel)

    def command_followers_only_on(self, length: int = 1, channel: CHANNELS_TYPE = None):
        self.command_followers_only(length, channel)

    def command_followers_only_off(self, channel: CHANNELS_TYPE = None):
        self.send_message("/followersoff", channel)

    def command_help(self, command: str = "", channel: CHANNELS_TYPE = None):
        self.send_message("/help {}".format(command), channel)

    def command_host(self, channel_name: str, channel: CHANNELS_TYPE = None):
        self.send_message("/host {}".format(channel_name), channel)

    def command_unhost(self, channel: CHANNELS_TYPE = None):
        self.send_message("/unhost", channel)

    def command_marker(self, description: str = "", channel: CHANNELS_TYPE = None):
        self.send_message("/marker {}".format(description), channel)

    def command_me(self, message: str, channel: CHANNELS_TYPE = None):
        self.send_message("/me <message>".format(message), channel)

    def command_mod(self, username: str, channel: CHANNELS_TYPE = None):
        self.send_message("/mod {}".format(username), channel)

    def command_unmod(self, channel: CHANNELS_TYPE = None):
        self.send_message("/unmod", channel)

    def command_mods(self, channel: CHANNELS_TYPE = None):
        self.send_message("/mods", channel)

    def command_raid(self, channel_name: str, channel: CHANNELS_TYPE = None):
        self.send_message("/raid {}".format(channel_name), channel)

    def command_unraid(self, channel: CHANNELS_TYPE = None):
        self.send_message("/unraid", channel)

    def command_slow(self, wait_time: float, channel: CHANNELS_TYPE = None):
        self.send_message("/slow {}".format(wait_time), channel)

    def command_subscribers(self, channel: CHANNELS_TYPE = None):
        self.send_message("/subscribers", channel)

    def command_subscribers_on(self, channel: CHANNELS_TYPE = None):
        self.command_subscribers(channel)

    def command_subscribers_off(self, channel: CHANNELS_TYPE = None):
        self.send_message("/subscribersoff", channel)

    def command_timeout(self, username: str, length: float, channel: CHANNELS_TYPE = None):
        self.send_message("/timeout {} {}".format(username, length), channel)

    def command_untimeout(self, username: str, channel: CHANNELS_TYPE = None):
        self.send_message("/untimeout {}".format(username), channel)

    def command_unique_chat(self, channel: CHANNELS_TYPE = None):
        self.send_message("/uniquechat", channel)

    def command_unique_chat_on(self, channel: CHANNELS_TYPE = None):
        self.command_unique_chat(channel)

    def command_unique_chat_off(self, channel: CHANNELS_TYPE = None):
        self.send_message("/uniquechatoff", channel)

    def command_vip(self, username: str, channel: CHANNELS_TYPE = None):
        self.send_message("/vip {}".format(username), channel)

    def command_vips(self, channel: CHANNELS_TYPE = None):
        self.send_message("/vips", channel)

    def command_w(self, username: str, message: str, channel: CHANNELS_TYPE = None):
        self.send_message("/w {} {}".format(username, message), channel)

    def on_message(self, message: str, username: str, channel: str, tags):
        pass

    def on_clear_chat(self, channel: str, tags, username: str = None):
        pass

    def on_clear_message(self, message: str, channel: str, tags):
        pass

    def on_host_start(self, target: str, viewers: int, channel: str):
        pass

    def on_host_end(self, viewers: int, channel: str):
        pass

    def on_user_join(self, username: str, channel: str):
        pass

    def on_user_leave(self, username: str, channel: str):
        pass

    def on_whisper(self, message: str, username: str, tags):
        pass

    def on_user_notice(self, channel: str, tags: dict, message: str = None):
        pass
