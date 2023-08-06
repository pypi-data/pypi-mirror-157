import TwitchPyRC.models.tag_models.base_tag_model as base_tag_model


class ClearMessage(base_tag_model.BaseTagModel):
    def __init__(self, **kwargs):
        """
        :param room_id:
        :param tmi_sent_ts:
        :param target_user_id: ID of user who has been timed out (or None if /clear was used)
        :param ban_duration: Duration of timeout in seconds (or None if /clear was used)
        """
        self.login = kwargs["login"]
        self.room_id = int(kwargs["room_id"])
        self.target_msg_id = kwargs["target_msg_id"]
        self.sent = self._to_timestamp(kwargs["tmi_sent_ts"])
