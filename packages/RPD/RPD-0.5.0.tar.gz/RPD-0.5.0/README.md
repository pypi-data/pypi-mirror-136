<h1 align="center">RPD</h1>

A asynchronous Discord API Wrapper for Python

## Features

- Sane Handling of 429s
- Customizable
- Gateway Support

## Installing

To Install RPD Just run the following command:

```py
pip install RPD
```

To install our speed requirements just run the following command:

```py
pip install RPD[speed]
```

## Example
This is a quick usecase example for the library!

```py
import rpd

bot = rpd.BotApp()

@bot.listen
async def on_ready():
    print("ready!")

bot.run("my_bot_token")
```

This is another example but with a prefixed command

```py
import rpd

bot = rpd.BotApp()

@bot.listen
async def on_ready():
    print("ready!")

@bot.listen
async def on_message(msg):
    if str(msg["content"]).startswith("!ping"):
        await bot.factory.create_message(msg["channel_id"], "pong!")

bot.run("my_bot_token")
```

## Useful Links

The RPD [Discord Server](https://discord.gg/cvCAwntVhm)
