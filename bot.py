# also work on reactionroles /selfroles
# and maybe api work with the coding academy for possible meme api.
# .draw file creates drawing
# help_<command_name> cmds
# note: IF F'NG STUPID TabError comes up, unindent and reindent all lines from command, one at a time.
# for welcome and ai-chat stuff, see if a channel with the keyword 'welcome', or 'ai-chat' exists, if yes, then post stuff accordingly there. If no, create those channels using user input. (prob try except for this)

#heres the link to add the testbot to the server for testing mod commands.
#https://discord.com/api/oauth2/authorize?bot_id=834282409032679460&permissions=523328&scope=bot

import discord
#discord lib (async lib)
# Note to self: when writing bot, make sure version of python is on 3.8.5+ bottom left of screen (vscode)
from discord.ext import commands, tasks, slash
import random
import os
from keep_alive import keep_alive
from itertools import cycle
import json
import traceback
import datetime
import asyncio
import sys
# from flask import Flask, render_template
# from oauth import Oauth
import requests
import aiosqlite
from prsaw import RandomStuff
import platform
from pathlib import Path
import motor.motor_asyncio
import cogs.utils.json_loader
from cogs.utils.mongo import Document
from cogs.utils.util import clean_code, Pag
import logging
import io
from flask import Flask, render_template
import pymongo
from pymongo import Mongobot
import contextlib
import io
import os
import logging
from prsaw import RandomStuff
import textwrap
from traceback import format_exception

cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")


async def get_prefix(bot, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)


intents = discord.Intents.all()  # Help command requires member intents
DEFAULTPREFIX = "!"
secret_file = cogs.utils.json_loader.read_json("secrets")
bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    owner_id=759919832539332639,
    help_command=None,
    intents=intents,
)  # change command_prefix='-' to command_prefix=get_prefix for custom prefixes
bot.config_token = secret_file["token"]
bot.connection_url = secret_file["mongo"]

bot.news_api_key = secret_file["news api"]
# bot.joke_api_key = secret_file["x-rapidapi-key"]
bot.api_key = secret_file['api_key']

logging.basicConfig(level=logging.INFO)

bot.DEFAULTPREFIX = DEFAULTPREFIX
bot.blacklisted_users = []
bot.muted_users = {}
bot.cwd = cwd

bot.version = "15"

bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.color_list = [c for c in bot.colors.values()]


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(
        f"-----\nLogged in as: {bot.user.name} : {bot.user.id}\n-----\nMy current prefix is: {bot.DEFAULTPREFIX}\n-----"
    )
    await bot.change_presence(
        activity=discord.Game(name="Cries in Binary | 00111010 00101000")
    )  # This changes the bots 'activity'

    for document in await bot.config.get_all():
        print(document)

    currentMutes = await bot.mutes.get_all()
    for mute in currentMutes:
        bot.muted_users[mute["_id"]] = mute

    print(bot.muted_users)

    print("Initialized Database\n-----")

rs = RandomStuff(async_mode = True, api_key = bot.api_key)

@bot.event
async def on_message(msg):
    # Ignore messages sent by yourself
    if msg.author.bot:
        return

    # A way to blacklist users from the bot by not processing commands
    # if the author is in the blacklisted_users list
    if msg.author.id in bot.blacklisted_users:
        return

    # Whenever the bot is tagged, respond with its prefix
    if msg.content.startswith(f"<@!{bot.user.id}>") and len(msg.content) == len(
        f"<@!{bot.user.id}>"
    ):
        data = await bot.config.find_by_id(msg.guild.id)
        if not data or "prefix" not in data:
            prefix = bot.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        await msg.channel.send(f"My prefix here is `{prefix}`", delete_after=15)
    if 'ai-chat' in msg.channel.name:
        if bot.user == msg.author:
            return
        response = await rs.get_ai_response(msg.content)
        await msg.reply(response)
    await bot.process_commands(msg)


@bot.command(name="eval", aliases=["exec"])
@commands.is_owner()
async def _eval(ctx, *, code):
    await ctx.reply("Let me evaluate this code for you! Won't be a sec")
    code = clean_code(code)

    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": bot,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message,
    }

    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
            )

            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"
    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))

    pager = Pag(
        timeout=100,
        entries=[result[i : i + 2000] for i in range(0, len(result), 2000)],
        length=1,
        prefix="```py\n",
        suffix="```",
    )

    await pager.start(ctx)

bot.load_extension("jishaku")

async def initialize():
	await bot.wait_until_ready()
	bot.db = await aiosqlite.connect("expData.db")
	await bot.db.execute("CREATE TABLE IF NOT EXISTS guildData (guild_id int, user_id int, exp int, PRIMARY KEY (guild_id, user_id))")

async def general_databases():
    await bot.wait_until_ready()
    bot.db1 = await aiosqlite.connect("General_db.db")
    await bot.db1.execute("CREATE TABLE IF NOT EXISTS suggestionchannel(guild_id int, suggestion_channel_id int, PRIMARY KEY (guild_id))")

@tasks.loop(seconds=10)
async def ch_pr():
    await bot.wait_until_ready()
    h = [1,2,3]
    h = random.choice(h)
    statuses=['ɢɪᴛʜᴜʙ','ᴘʏᴛʜᴏɴ 3.8│ c!help', f'in {len(bot.guilds)} servers!', 'Replit', 'Discord.py','you.','this server.','mods.','your mom.','a drug dealer.','karens','Dream','The Dream SMP','Dom (You probably Dont know him)', 'https://tinyurl.com/cafebotgoyee']
    status=random.choice(statuses)
    if h == 1:
        await bot.change_presence(activity=discord.Game(name=status))
    elif h == 2:
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name=status))
    else:
        await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=status))
ch_pr.start()

if __name__ == "__main__":
    # When running this file, if it is the 'main' file
    # I.E its not being imported from another python file run this
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["menudocs"]
    bot.config = Document(bot.db, "config")
    bot.mutes = Document(bot.db, "mutes")
    bot.warns = Document(bot.db, "warns")
    bot.invites = Document(bot.db, "invites")
    bot.command_usage = Document(bot.db, "command_usage")
    bot.reaction_roles = Document(bot.db, "reaction_roles")

    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(bot.config_token)
    bot.loop.create_task(initialize())
    bot.loop.create_task(general_databases())
    asyncio.run(bot.db.close())
    asyncio.run(bot.db1.close())