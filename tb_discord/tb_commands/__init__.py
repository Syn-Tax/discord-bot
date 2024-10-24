"""Collect all data from tb_command groups into a single interface for bot usage"""

import tb_discord.tb_commands.info
import tb_discord.tb_commands.mission_planning
import tb_discord.tb_commands.bot_management
import tb_discord.tb_commands.roles
import tb_discord.tb_commands.lesson_tracking
import tb_discord.tb_commands.qotds


__all__ = ["command_list"]


command_list = (
    info.command_list
    + mission_planning.command_list
    + bot_management.command_list
    + roles.command_list
    + lesson_tracking.command_list
    + qotds.command_list
)
