"""Coalesce all discord-related towerbot scripts"""

from discord.ext.commands import Bot
from discord import Intents

__all__ = ["bot"]

intents = Intents.none()
intents.guilds = True
intents.members = True
intents.guild_messages = True
intents.message_content = True

bot = Bot(command_prefix="t?", intents=intents)


# Imported below top to allow for bot to init
import tb_discord.tb_events
from tb_discord import tb_commands

# from tb_discord.tb_commands.bot_management import sync_command_tree

for command in tb_commands.command_list:
    bot.tree.add_command(command)
    # bot.add_command(command)

# bot.add_command(sync_command_tree)
