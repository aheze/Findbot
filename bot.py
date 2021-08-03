# bot.py - test

from logging import error
import os
from asyncio.base_events import Server
import discord

from discord.ext import commands
from dotenv import load_dotenv
import asyncio

import z_About
import Misc
import Moderation
import Permissions
import Reactions
import ReactionRoles
import ReactionActions
import TimedActions
import Tutorials
import Help
import Censoring
import Stats
import ServerStatus
import Polls
import Config

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.messages = True
intents.voice_states = True
intents.invites = True

activity = discord.Game(name="getfind.app")
bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    z_About.PREFIX), activity=activity, intents=intents, help_command=None)

# Emoji
RED = "<:Red:860713765107400714>"
GREEN = "<:Green:860713764742496258>"
RED_ID = "860713765107400714"
GREEN_ID = "860713764742496258"

# IDs
FINDBOT_ID = "784531493204262942"
FINDBOT_TEST_ID = "860667927345496075"

# @bot.command(name="deleteallemojis")
# async def delete_all_emojis(ctx):
#     for emoji in ctx.guild.emojis:
#         await emoji.delete()

@bot.command(name='ping')
async def ping(ctx):
    await Misc.ping(ctx)


@bot.command(name='dance')
async def dance(ctx):
    await Misc.dance(ctx)


@bot.command(name='pfp')
async def get_pfp(ctx, user: discord.User):
    await Misc.get_pfp(ctx, user)


@bot.command(name='help')
async def help(ctx, *args):
    await Help.help(bot, ctx, args)


@bot.command(name='resethelp')
async def remove_lingering_helps(ctx):
    await Help.remove_lingering_helps()


@bot.command(name='send')
async def send(ctx, channel: discord.TextChannel, *args):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await Misc.send(channel, args)


@bot.command(name='setpollcolor')
async def set_poll_color(ctx, color):
    await Polls.set_poll_color(ctx, color)


@bot.command(name='poll')
async def make_poll(ctx, *args):
    await Polls.make_poll(bot, ctx, args)


@bot.command(name='color')
async def get_color(ctx, color: str):
    await Misc.get_color(ctx, color)


@bot.command(name='how')
async def send_tutorial(ctx, tutorial_name):
    await Tutorials.send_tutorial(bot, ctx, tutorial_name)


@bot.command(name='unhow')
async def send_tutorial(ctx, specific_command_name=None):
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


@bot.command(name='lock')
async def mute(ctx, channel: discord.TextChannel = None):
    if Permissions.check_no_permissions(ctx.author): return
    await Moderation.lock(ctx, channel)


@bot.command(name='unlock')
async def mute(ctx, channel: discord.TextChannel = None):
    if Permissions.check_no_permissions(ctx.author): return
    await Moderation.unlock(ctx, channel)


@bot.command(name='givemember')
async def give_all_member(ctx):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await Moderation.give_all_member(ctx)


@bot.command(name='setclaim')
async def set_claim_role(ctx, user: discord.User, emoji_role_name: str, in_channel: discord.TextChannel, *args):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await Reactions.set_claim_role(bot, ctx, user, emoji_role_name, in_channel, args)


@bot.command(name='reactroles')
async def set_reaction_roles(ctx, message_link, *reaction_roles):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await ReactionRoles.set_reaction_roles(bot, ctx, message_link, reaction_roles)

# @bot.command(name='setmodlog')
# async def set_modlog(ctx, channel: discord.TextChannel):
#     if Permissions.check_no_admin_permissions(ctx.author): return
#     await Config.set_modlog(ctx, channel)


@bot.command(name='config')
async def configurate(ctx, name, channel: discord.TextChannel):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await Config.configurate(ctx, name, channel)


@bot.command(name='eventleaderboard')
async def set_modlog(ctx, ping=None):
    if Permissions.check_no_permissions(ctx.author): return
    await ReactionActions.event_leaderboard(bot, ctx, ping)


@bot.command(name='updatestats')
async def update_stats(ctx):
    await Stats.update(ctx)


@bot.event
async def on_message(message):
    if message.channel.id == z_About.IGNORED_CHANNEL_ID: return
    if message.author == bot.user: return
    await Polls.check_reply(bot, message)
    if Permissions.check_no_admin_permissions(message.author) == False:
        # Needed to allow other commands to work
        await bot.process_commands(message)
    else:
        await Censoring.check_censor(bot, message)
        # Needed to allow other commands to work
        await bot.process_commands(message)


@bot.event
async def on_raw_message_edit(payload):
    await Censoring.check_edit_censor(bot, payload)


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
    await ServerStatus.on_member_join(bot, member)


@bot.event
async def on_member_remove(member):
    await ServerStatus.on_member_remove(bot, member)


@bot.event
async def on_voice_state_update(member, before, after):
    await ServerStatus.on_voice_state_update(bot, member, before, after)


@bot.event
async def on_invite_create(invite):
    await ServerStatus.on_invite_create(bot, invite)


@bot.event
async def on_ready():
    print(f"Ready - {z_About.INFO}!")
    asyncio.create_task(TimedActions.check_timed_actions(bot))
    asyncio.create_task(Help.clean_up_helps())


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You need a higher role ;-;')


bot.run(TOKEN)
