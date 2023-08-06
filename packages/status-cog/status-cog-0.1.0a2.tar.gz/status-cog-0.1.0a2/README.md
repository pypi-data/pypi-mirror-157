# StatusCog
## Installation
```commandline
pip install status-cog
```

## Usage
```python
import os
from discord.ext import commands

os.environ["status_cog_webhook_url"] = None # WEBHOOK URL HERE
os.environ["status_cog_message_id"] = None # Message ID here if you want the bot to edit the previous message (can also be None)

bot = commands.Bot(command_prefix="!")
bot.load_extension("status_cog")

bot.run()
```

## Commands
### [prefix]maintenance
Enables maintenance mode, when the bot shuts off it won't send an offline message but a maintenance message showing that this shutdown was planned.