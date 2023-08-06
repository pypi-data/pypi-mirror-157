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