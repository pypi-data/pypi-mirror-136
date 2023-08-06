<h1 align='center'>RPD</h1>

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

For voice support run the following command:

```py
pip install RPD[audio]
```

## Example
This is a quick usecase example for the library!

```py
import rpd

bot = rpd.BotApp()

@bot.event
async def on_ready():
    print('ready!')

bot.run('my_bot_token')
```

This is another example but with a prefixed command

```py
import rpd

bot = rpd.BotApp()

@bot.event
async def on_ready():
    print('ready!')

@bot.event
async def on_message(msg):
    if msg.content.startswith('!ping'):
        await msg.reply('pong!')

bot.run('my_bot_token')
```

## Useful Links

The RPD [Discord Server](https://discord.gg/cvCAwntVhm)
