import typing

import TwitchPyRC.models.tag_models.base_tag_model as base_tag_model
import TwitchPyRC.models.badge as badge_model


class Whisper(base_tag_model.BaseTagModel):
    def __init__(self, **kwargs):
        self.color = kwargs.get("color")
        self.display_name = kwargs.get("display_name")
        self.emotes = kwargs.get("emotes")
        self.message_id = kwargs.get("message_id")
        self.thread_id = kwargs.get("thread_id")
        self.turbo = self._to_bool(kwargs.get("turbo"))
        self.user_id = self._to_int(kwargs.get("user_id"))
        self.user_type = kwargs.get("user_type")

        if kwargs.get("badges", "") == "":
            self.badges = []
        else:
            self.badges = [badge_model.Badge.from_string(b) for b in kwargs.get("badges", "").split(",")]

    def color_to_rgb(self) -> typing.Tuple[int, int, int]:
        return tuple(int(self.color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
