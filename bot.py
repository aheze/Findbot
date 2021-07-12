# bot.py - test

INFO = "Test 3"
PREFIX = ","

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
import Tutorials
import Help


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True

activity = discord.Game(name="getfind.app")
bot = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), activity=activity, intents=intents, help_command=None)

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

@bot.command(name='help')
async def get_pfp(ctx):
    print("help...")
    await Help.help(bot, ctx)

@bot.command(name='color')
async def get_color(ctx, color: str):
    await Misc.get_color(ctx, color)

@bot.command(name='how')
async def send_tutorial(ctx, tutorial_name):
    await Tutorials.send_tutorial(bot, ctx, tutorial_name)
    
@bot.command(name='unhow')
async def send_tutorial(ctx, specific_command_name = None):
    await Tutorials.unsend_latest_tutorial(bot, ctx, specific_command_name)

@bot.command(name='react')
async def react(ctx, message_id, reaction):
    if Permissions.check_no_permissions(ctx.author): return
    await Reactions.react(bot, ctx, message_id, reaction)

@bot.command(name='clearreacts')
async def clear_reacts(ctx, message_link):
    if Permissions.check_no_permissions(ctx.author): return
    await Reactions.clear_reacts(bot, message_link)

@bot.command(name='unmute')
async def unmute(ctx, user: discord.User, *args):
    if Permissions.check_no_permissions(ctx.author): return
    await Moderation.unmute(bot, ctx, user, args)

@bot.command(name='mute')
async def mute(ctx, user: discord.User, *args):
    if Permissions.check_no_permissions(ctx.author): return
    await Moderation.mute(bot, ctx, user, args)

@bot.command(name='ban')
async def ban(ctx, user: discord.User, *args):
    if Permissions.check_no_permissions(ctx.author): return
    await Moderation.ban(bot, ctx, user, args)

@bot.command(name='unban')
async def unban(ctx, user: discord.User, *args):
    if Permissions.check_no_permissions(ctx.author): return
    await Moderation.unban(bot, ctx, user, args)

@bot.command(name='givemember')
async def give_all_member(ctx):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await Moderation.give_all_member(ctx)

@bot.command(name='setclaim')
async def set_claim_role(ctx, user: discord.User, emoji_name: str, role_name: str, in_channel: discord.TextChannel, *args):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await Reactions.set_claim_role(bot, ctx, user, emoji_name, role_name, in_channel, args)

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
    if Permissions.check_no_admin_permissions(message.author) == False: 
        await bot.process_commands(message) # Needed to allow other commands to work
        return
    else:
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
async def on_member_join(member):
    await Moderation.give_member_role(member)

@bot.event
async def on_raw_message_delete(payload):
    await Moderation.handle_message_delete(bot, payload)

@bot.event
async def on_ready():
    print(f"Ready - {INFO}!")
    await TimedActions.check_timed_actions(bot)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You need a higher role ;-;')


bot.run(TOKEN)


