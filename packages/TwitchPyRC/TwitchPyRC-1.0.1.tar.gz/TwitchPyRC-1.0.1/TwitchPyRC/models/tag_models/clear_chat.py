import TwitchPyRC.models.tag_models.base_tag_model as base_tag_model


class ClearChat(base_tag_model.BaseTagModel):
    def __init__(self, **kwargs):
        """
        :param room_id:
        :param tmi_sent_ts:
        :param target_user_id: ID of user who has been timed out (or None if /clear was used)
        :param ban_duration: Duration of timeout in seconds (or None if /clear was used)
        """
        self.room_id = int(kwargs["room_id"])
        self.sent = self._to_timestamp(kwargs["tmi_sent_ts"])
        self.target_user_id = kwargs.get("target_user_id", None)
        self.ban_duration = kwargs.get("ban_duration", None)

        if self.target_user_id is not None:
            self.target_user_id = int(kwargs["target_user_id"])

        if self.ban_duration is not None:
            self.ban_duration = int(kwargs["ban_duration"])
