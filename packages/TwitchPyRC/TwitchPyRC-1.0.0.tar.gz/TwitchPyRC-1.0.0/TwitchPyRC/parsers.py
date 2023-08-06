import TwitchPyRC.models.message_model as message_model


def parse_tags(tags: str) -> dict:
    parsed = {}
    if tags.startswith("@"):
        tags = tags[1:]

    for var in tags.rstrip(" ").replace("\\s", " ").split(";"):
        key, value = var.split("=")
        parsed[key] = value

    return parsed


def create_tags(data: dict) -> str:
    result = "@"

    keys = list(data.keys())
    keys.sort()

    for key in keys:
        result += "{}={};".format(key, data[key])

    return result.rstrip(";").replace(" ", "\\s") + " "


def parse_message(message: str) -> message_model.Message:
    if message.startswith("@"):
        tags = parse_tags(message[:message.index(" ")])
    else:
        tags = {}

    message = message[message.index(":") + 1:]

    source_component = message[:message.index(" ")]
    if "!" in source_component:
        nickname, host = source_component.split("!")
    else:
        nickname, host = None, None

    message = message[message.index(" ") + 1:]

    try:
        command = message[:message.index(":")].rstrip(" ").split(" ")
        args = message[message.index(":") + 1:]

    except ValueError:
        command = message.rstrip(" ").split(" ")
        args = None

    return message_model.Message(tags, nickname, host, command, args)
