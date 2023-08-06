# TwitchPyRC
Yet another generic Twitch IRC interface that probably works

## Installation
```shell
pip install TwitchPyRC
```

You will also need an oauth token which can be obtained from https://twitchapps.com/tmi/. 
Simply replace `[oauth token]` in code samples with your own token.

## Usage
TwitchPyRC can be used in a few different ways. The easiest being as follows:
```python
import TwitchPyRC

bot = TwitchPyRC.CommandBot("[oauth token]", ["channel_1", "channel_2", "channel_3"])


@bot.command(["!test", TwitchPyRC.Variable("value"), TwitchPyRC.Variable("value2", int, default=5)], cooldown=5)
def my_command(value, value2):
    print("Test command used with arguments: ", value, value2)


bot.start()
```

It is that easy! 

More documentation coming soon
