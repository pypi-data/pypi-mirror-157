import typing

import TwitchPyRC.models.tag_models.base_tag_model as base_tag_model
import TwitchPyRC.models.badge as badge_model


class MessageSent(base_tag_model.BaseTagModel):
    def __init__(self, **kwargs):
        self.badge_info = kwargs.get("badge_info")
        self.client_nonce = kwargs.get("client_nonce")
        self.color = kwargs.get("color")
        self.display_name = kwargs.get("display_name")
        self.emotes = kwargs.get("emotes")
        self.first_msg = self._to_bool(kwargs.get("first_msg"))
        self.flags = kwargs.get("flags")
        self.id = kwargs.get("id")
        self.mod = self._to_bool(kwargs.get("mod"))
        self.room_id = self._to_int(kwargs.get("room_id"))
        self.subscriber = self._to_bool(kwargs.get("subscriber"))
        self.sent = self._to_timestamp(kwargs.get("tmi_sent_ts"))
        self.turbo = self._to_bool(kwargs.get("turbo"))
        self.user_id = self._to_int(kwargs.get("user_id"))
        self.user_type = kwargs.get("user_type")

        if kwargs.get("badges", "") == "":
            self.badges = []
        else:
            self.badges = [badge_model.Badge.from_string(b) for b in kwargs.get("badges", "").split(",")]

    def color_to_rgb(self) -> typing.Tuple[int, int, int]:
        return tuple(int(self.color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
