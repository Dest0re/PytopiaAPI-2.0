# PytopiaAPI-2.0
Python API-wrapper for the Utopia Ecosystem.

## How to install?
Well, you can only install this package manually for now, but it will be on PyPi later.

## How to use?
```py
import pytopiaAPI

client = pytopiaAPI.Client()


@client.event
def on_ready():
    print('Ready!')  # This text will be printed when client getting ready.


@client.event
def on_message(message):
    print(message)  # This function will print every new message.
    message.channel.send('Hello World!')  # Sending a "Hello World" message in message channel.


client.run(%YOURUTOPIATOKEN%)  # Running client.
```

## Why `2.0`?
The 1.x version can be found here: https://github.com/Dest0re/PytopiaAPI.

It's no longer supported.
