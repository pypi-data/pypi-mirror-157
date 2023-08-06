# -*- coding: utf-8 -*-

"""
status_cog.cog
~~~~~~~~~~~~~~

The cog implementation to load into the bot

:copyright: (c) 2022 Pjay
:license: MIT, see LICENSE for more details

"""

import atexit
import inspect
import os
import aiohttp
import discord
from discord.ext import commands

__all__ = (
    "StatusCog",
    "setup"
)


class StatusCog(commands.Cog):
    """
    The front end cog for the events
    """

    def __init__(self, bot: commands.Bot):  # pylint: disable=missing-function-docstring
        self.bot = bot
        self.maintenance_mode = False
        self.style = str(os.environ["status_cog_style"])
        self.embeds = {
            "1": {
                "online": discord.Embed(
                    title="Bot Status 🟢",
                    description="Bot is now online!",
                    color=discord.Colour.green()
                ),
                "maintenance": discord.Embed(
                    title="Bot Status 🟡",
                    description="The bot is going offline for maintenance!",
                    colour=discord.Colour.gold()
                ),
                "offline": discord.Embed(
                    title="Bot Status 🔴",
                    description="The bot is offline, please wait until it is back online again.",
                    colour=discord.Colour.red()
                )
            },
            "2": {
                "online": discord.Embed(
                    title="Online",
                    description="The bot is online",
                    color=discord.Colour.blurple()
                ),
                "maintenance": discord.Embed(
                    title="Offline",
                    description="The bot is offline due to maintenance",
                    color=discord.Colour.gold()
                ),
                "offline": discord.Embed(
                    title="Offline",
                    description="The bot is offline due to unkown causes",
                    color=discord.Colour.red()
                )
            }
        }

        atexit.register(self.on_exit)

    def on_exit(self):
        """
        When the python interpreter exits this function gets called. It either sends a shutdown or
        maintenance message depending on the state that the self.maintenance_mode variable is in.
        """

        webhook = discord.Webhook.from_url(
            os.environ.get("status_cog_webhook_url"),
            adapter=discord.RequestsWebhookAdapter()
        )

        if self.maintenance_mode:
            try:
                webhook.edit_message(
                    message_id=int(os.environ.get("status_cog_message_id")),
                    embed=self.embeds[self.style]["maintenance"],
                    username=self.bot.user.name
                )
            except TypeError:
                webhook.send(
                    embed=self.embeds[self.style]["maintenance"],
                    username=self.bot.user.name
                )
        else:
            try:
                webhook.edit_message(
                    message_id=int(os.environ.get("status_cog_message_id")),
                    embed=self.embeds[self.style]["offline"],
                    username=self.bot.user.name
                )
            except TypeError:
                webhook.send(
                    embed=self.embeds[self.style]["offline"],
                    username=self.bot.user.name
                )

    @commands.Cog.listener()
    async def on_ready(self):  # pylint: disable=missing-function-docstring
        """
        When the bot is ready it edits the message that the bot is online
        """

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(
                os.environ.get("status_cog_webhook_url"),
                adapter=discord.AsyncWebhookAdapter(session)
            )
            try:
                await webhook.edit_message(
                    message_id=int(os.environ.get("status_cog_message_id")),
                    embed=self.embeds[self.style]["online"],
                    username=self.bot.user.name
                )
            except TypeError:
                await webhook.send(
                    embed=self.embeds["online"],
                    username=self.bot.user.name
                )

    @commands.command()
    @commands.is_owner()
    async def maintenance(self, ctx: commands.Context):
        """
        Enables maintenance mode and does not send a red but a yellow announcement
        """

        self.maintenance_mode = not self.maintenance_mode
        await ctx.send(f"Maintenance is set to `{self.maintenance_mode}`")


async def async_setup(bot: commands.Bot):
    """
    The setup function that adds StatusCog to the bot but as a coroutine
    """

    await bot.add_cog(StatusCog(bot))


def setup(bot: commands.Bot):  # pylint: disable=inconsistent-return-statements
    """
    The setup function that adds StatusCog to the bot
    """

    if inspect.iscoroutinefunction(bot.add_cog):
        return async_setup(bot)

    bot.add_cog(StatusCog(bot))
