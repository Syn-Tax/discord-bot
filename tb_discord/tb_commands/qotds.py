"""Towerbot commands dealing with Questions of the Day"""

from discord import app_commands, Interaction, Embed, Colour, ChannelType
from discord.ext import tasks
import datetime
import random

from configs import configs
from tb_discord.tb_commands.filters import check_is_instructor
from tb_db import sql_op
from tb_discord import bot


__all__ = ["command_list"]


@app_commands.command()
@app_commands.choices(
    branch=[
        app_commands.Choice(name="ATSA", value=0),
        app_commands.Choice(name="TCA", value=1),
    ]
)
@check_is_instructor()
async def add_question(inter: Interaction, branch: int, question: str, answer: str):
    if len(question) == 0:
        await inter.response.send_message("Question cannot be empty", ephemeral=True)

    if len(answer) == 0:
        await inter.response.send_message("Answer cannot be empty", ephemeral=True)

    sql_op(
        "INSERT INTO questions (branch, question, answer) VALUES (%s, %s, %s)",
        (branch, question, answer),
    )

    await inter.response.send_message("Question sucessfully added")


@app_commands.command()
@app_commands.choices(
    branch=[
        app_commands.Choice(name="ATSA", value=0),
        app_commands.Choice(name="TCA", value=1),
    ]
)
@check_is_instructor()
async def list_questions(inter: Interaction, branch: int):
    res = sql_op(
        "SELECT branch, question, answer FROM questions WHERE branch = %s",
        (branch,),
        fetch_all=True,
    )

    embed = Embed(title="QOTDs", colour=Colour.green())
    embed.add_field(name="Question", value="\n".join([row[1] for row in res]))
    embed.add_field(name="Answer", value="\n".join([row[2] for row in res]))

    embed.set_footer(text=f"Fetched {len(res)} questions")

    await inter.response.send_message(embed=embed)


@tasks.loop(
    time=datetime.datetime.strptime(configs.qotd_time, "%H:%M")
    .replace(tzinfo=datetime.timezone.utc)
    .time()
)
async def qotd(inter: Interaction):
    for branch, channel_id in enumerate(configs.qotd_channels):
        channel = bot.get_channel(channel_id)

        role = configs.qotd_roles[branch]

        # send today's QOTD
        name = f"QOTD {datetime.datetime.now().strftime('%d/%m/%y')}"

        # skip if QOTD already posted
        if name in [t.name for t in channel.threads]:
            continue

        questions = sql_op(
            "SELECT branch, times, question, answer FROM questions WHERE branch = %s AND times = (SELECT MIN(times) FROM questions WHERE branch = %s)",
            (branch, branch),
            fetch_all=True,
        )

        question = random.choice(questions)

        sql_op(
            "UPDATE questions SET times = times + 1 WHERE question = %s;",
            (question[2],),
        )

        message = f"""{question[2]}\n\nPlease react :eyes: to this post if you just want to see what people say. Thank you!\n\nAs always, remember to `||spoiler your answers||`\n||<@&{role}>||"""

        if channel.type == ChannelType.text:
            thread = await channel.create_thread(
                name=name,
            )
            await thread.send(message)

        elif channel.type == ChannelType.forum:
            thread = await channel.create_thread(name=name, content=message)

        # post answer to yesterday's QOTD
        # yes I know this is kinda jank but it shouldn't have any actual impact
        name = f"QOTD {(datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d/%m/%y')}"
        for thread in channel.threads:
            if thread.name != name:
                continue

            question = (
                thread.starter_message
                if thread.starter_message
                else await thread.history(oldest_first=True).__anext__()
            ).content

            question = question.split("\n")[0]

            answer = sql_op(
                "SELECT branch, question, answer FROM questions WHERE branch = %s AND question = %s;",
                (branch, question),
            )

            message = f"""It is time for the answer!!\n\n{answer[2]}"""

            await thread.send(message)


command_list = [add_question, list_questions]
