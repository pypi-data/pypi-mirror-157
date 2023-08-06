class Badge:
    def __init__(self, badge: str, version: int):
        self.badge = badge
        self.version = version

    @classmethod
    def from_string(cls, badge: str):
        return cls(*badge.replace("\\", "/").split("/"))

    def __repr__(self):
        return "<Badge {}/{}>".format(self.badge, self.version)
