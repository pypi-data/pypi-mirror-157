# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['status_cog']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'discord.py>=1.7.3,<2.0.0']

setup_kwargs = {
    'name': 'status-cog',
    'version': '0.1.0a1',
    'description': 'Shows the bot status in your discord server.',
    'long_description': '# StatusCog\n## Installation\n```commandline\npip install status-cog\n```\n\n## Usage\n```python\nimport os\nfrom discord.ext import commands\n\nos.environ["status_cog_webhook_url"] = None # WEBHOOK URL HERE\nos.environ["status_cog_message_id"] = None # Message ID here if you want the bot to edit the previous message (can also be None)\n\nbot = commands.Bot(command_prefix="!")\nbot.load_extension("status_cog")\n\nbot.run()\n```',
    'author': 'Pjay',
    'author_email': 'Pjay1@tutanota.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/1Pjay/StatusCog.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
