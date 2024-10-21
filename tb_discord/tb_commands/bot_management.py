"""Towerbot commands dealing with bot management"""

from discord import app_commands, Interaction
from tb_discord.tb_commands.filters import check_is_owner
from tb_discord import bot


__all__ = ["command_list"]


@app_commands.command()
# @check_is_owner()
async def ping(interaction: Interaction):
    latency = str(bot.latency)[:-13]
    await interaction.response.send_message(f"Pong! Ping is {latency}s.")


@app_commands.command()
# @bot.command()
# @check_is_owner()
async def sync_command_tree(ctx):
    await bot.tree.sync()
    await ctx.send("Tree synced.")


# @app_commands.command()
@bot.command()
# @check_is_owner()
async def sync_command_tree(ctx):
    await bot.tree.sync()
    await ctx.send("Tree synced.")


command_list = [ping]
