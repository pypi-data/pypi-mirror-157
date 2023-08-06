import typing

import TwitchPyRC.models.tag_models.base_tag_model as base_tag_model
import TwitchPyRC.models.badge as badge_model


class MessageSent(base_tag_model.BaseTagModel):
    def __init__(self, **kwargs):
        self.badge_info = kwargs["badge_info"]
        self.badges = [badge_model.Badge.from_string(b) for b in kwargs["badges"].split(",")]
        self.client_nonce = kwargs["client_nonce"]
        self.color = kwargs["color"]
        self.display_name = kwargs["display_name"]
        self.emotes = kwargs["emotes"]
        self.first_msg = self._to_bool(kwargs["first_msg"])
        self.flags = kwargs["flags"]
        self.id = kwargs["id"]
        self.mod = self._to_bool(kwargs["mod"])
        self.room_id = int(kwargs["room_id"])
        self.subscriber = self._to_bool(kwargs["subscriber"])
        self.sent = self._to_timestamp(kwargs["tmi_sent_ts"])
        self.turbo = self._to_bool(kwargs["turbo"])
        self.user_id = int(kwargs["user_id"])
        self.user_type = kwargs["user_type"]

    def color_to_rgb(self) -> typing.Tuple[int, int, int]:
        return tuple(int(self.color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
