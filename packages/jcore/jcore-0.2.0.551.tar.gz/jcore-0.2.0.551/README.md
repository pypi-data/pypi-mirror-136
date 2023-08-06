# J-Core

[![Python Version](https://img.shields.io/badge/Python%20Version-3.7%20%7C%203.8%20%7C%203.9-brightgreen)](https://python.org)    [![PyPI version](https://badge.fury.io/py/jcore@2x.svg)](https://badge.fury.io/py/jcore)

This framework is a simple wrapper for creating [Twitch](https://twitch.tv) bots using Python. 
The [Jarvis chatbot for twitch and discord](https://jarvis.bot) has been built using the J-Core framework for it's Twitch components. 

A full set of documentation is still being developed, however, a getting started guide is outlined below.

## Getting started

### Prerequisites
To get started creating a bot using the J-Core framwork is pretty simple, but it does require that you have [Python](https://python.org) installed on your computer.  
Some operating systems come with python pre-installed (e.g. MacOS and most Linux systems), but if you're on Windows, you will need to [download Python](https://python.org/download) first to create a bot.  
Once you have installed Python, you can use `pip` to install the J-Core framework and start creating your first bot.

### Installation
To install the J-Core framework using pip:
```pip install jcore```

To install using this repository:
1. clone the directory using `git clone`
2. navigate into the directory and use `pip install`


### Creating a Simple Bot
To create a simple bot, start by creating a new python file called `simple_bot.py` and copy the code below into the file.
```python
import asyncio
import jcore
from jcore.message import CommandMessage

class SimpleBot(jcore.Client):

    async def on_command(self, message: CommandMessage):
        if message.KEYWORD == "hi":
            await message.send(f"hello {message.display_name}")


if __name__ == "__main__":
    client = SimpleBot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.run())
    loop.close()
```

Next, create a file called `config.json` and copy the following snippet into the file.
```json
{
    "nick": "<nick>",
    "token": "<token>",
    "channels": [
        "<channel>",
        "<channel>",
        "<channel>"
    ]
}
```

Replace:
- `<nick>` with the username of your bot account. 
- `<token>` with the oauth token for your bot. Refer to the [Twitch Documentation - Getting Tokens](https://dev.twitch.tv/docs/authentication#getting-tokens) for more information about generating an oauth token.
- `<channel>` with the channels you want to connect to.

Once all the values have been set, you can start your bot using:
```bash
python3 simple_bot.py
```
or
```batch
py simple_bot.py
```

### Adding Logging
If you need to view the logging output of from the framework for your bot, you can configure logging by adding the logging import to the top of your file:
```python
import asyncio
import jcore
from jcore.message import CommandMessage
import logging
```

Then update the main section of your code to the following:
```python
if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    client = SimpleBot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(client.run())
    loop.close()
```

For more information on using the logging library, refer to the [python logging documentation](https://docs.python.org/3/library/logging.html).

### Examples
These examples above and more can be found in the [examples](https://github.com/cubbei/jcore/tree/master/examples) folder. 

### Support
If you require any further support, please join the [discord](https://jarvis.bot/discord) and seek help from the commuity. 