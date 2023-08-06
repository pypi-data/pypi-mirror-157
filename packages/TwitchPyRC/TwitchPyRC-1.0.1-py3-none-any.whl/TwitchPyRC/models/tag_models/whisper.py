import typing

import TwitchPyRC.models.tag_models.base_tag_model as base_tag_model
import TwitchPyRC.models.badge as badge_model


class Whisper(base_tag_model.BaseTagModel):
    def __init__(self, **kwargs):
        self.badges = [badge_model.Badge.from_string(b) for b in kwargs["badges"].split(",")]
        self.color = kwargs["color"]
        self.display_name = kwargs["display_name"]
        self.emotes = kwargs["emotes"]
        self.message_id = kwargs["message_id"]
        self.thread_id = kwargs["thread_id"]
        self.turbo = self._to_bool(kwargs["turbo"])
        self.user_id = int(kwargs["user_id"])
        self.user_type = kwargs["user_type"]

    def color_to_rgb(self) -> typing.Tuple[int, int, int]:
        return tuple(int(self.color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
