# bot.py - test
# version 1

from logging import error
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
import asyncio

import Misc
import Moderation
import Permissions
import Reactions
import ReactionRoles
import ReactionActions
import TimedActions


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True

activity = discord.Game(name="getfind.app")
bot = commands.Bot(command_prefix=',', activity=activity, intents=intents)

# Emoji
RED = "<:Red:860713765107400714>"
GREEN = "<:Green:860713764742496258>"
RED_ID = "860713765107400714"
GREEN_ID = "860713764742496258"

# IDs
FINDBOT_ID = "784531493204262942"
FINDBOT_TEST_ID = "860667927345496075"

@bot.command(name='ping')
async def ping(ctx):
    await Misc.ping(ctx)

@bot.command(name='pfp')
async def get_pfp(ctx, user: discord.User):
    await Misc.get_pfp(ctx, user)

@bot.command(name='react')
async def react(ctx, message_id, reaction):
    if Permissions.check_no_permissions(ctx.author): return
    await Reactions.react(bot, ctx, message_id, reaction)

@bot.command(name='clearreacts')
async def clear_reacts(ctx, message_link):
    if Permissions.check_no_permissions(ctx.author): return
    await Reactions.clear_reacts(bot, message_link)

@bot.command(name='unmute')
async def unmute(ctx, user: discord.User, reason = ""):
    if Permissions.check_no_permissions(ctx.author): return
    await Moderation.unmute(bot, ctx, user, reason)

@bot.command(name='mute')
async def mute(ctx, user: discord.User, *args):
    if Permissions.check_no_permissions(ctx.author): return
    await Moderation.mute(bot, ctx, user, args)

@bot.command(name='reactroles')
async def set_reaction_roles(ctx, message_link, *reaction_roles):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await ReactionRoles.set_reaction_roles(bot, ctx, message_link, reaction_roles)

@bot.command(name='setmodlog')
async def set_modlog(ctx, channel: discord.TextChannel):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await Moderation.set_modlog(ctx, channel)

@bot.event
async def on_message(message):
    if message.author == bot.user: return

    await Moderation.check_censor(bot, message)
    await bot.process_commands(message) # Needed to allow other commands to work

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.user_id) == FINDBOT_TEST_ID or str(payload.user_id) == FINDBOT_ID:
        return
    await ReactionActions.determine_reaction_action(bot, payload, "add")

@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.user_id) == FINDBOT_TEST_ID or str(payload.user_id) == FINDBOT_ID:
        return
    await ReactionActions.determine_reaction_action(bot, payload, "remove")

@bot.event
async def on_ready():
    print("Ready to test!")
    await TimedActions.check_timed_actions(bot)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You need a higher role ;-;')


bot.run(TOKEN)


