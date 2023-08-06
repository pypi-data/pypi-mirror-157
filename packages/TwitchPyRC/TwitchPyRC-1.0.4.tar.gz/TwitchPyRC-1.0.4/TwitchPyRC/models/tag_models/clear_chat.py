import TwitchPyRC.models.tag_models.base_tag_model as base_tag_model


class ClearChat(base_tag_model.BaseTagModel):
    def __init__(self, **kwargs):
        """
        :param room_id:
        :param tmi_sent_ts:
        :param target_user_id: ID of user who has been timed out (or None if /clear was used)
        :param ban_duration: Duration of timeout in seconds (or None if /clear was used)
        """
        self.room_id = self._to_int(kwargs.get("room_id"))
        self.sent = self._to_timestamp(kwargs.get("tmi_sent_ts"))
        self.target_user_id = self._to_int(kwargs.get("target_user_id"))
        self.ban_duration = self._to_int(kwargs.get("ban_duration"))
