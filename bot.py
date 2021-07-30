# bot.py - test

from logging import error
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv
import asyncio

import About
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
import Utilities
import Polls

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.messages = True

activity = discord.Game(name="getfind.app")
bot = commands.Bot(command_prefix=commands.when_mentioned_or(About.PREFIX), activity=activity, intents=intents, help_command=None)

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
    if args:
        message = " ".join(args)
        await channel.send(message)

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

@bot.command(name='eventleaderboard')
async def set_modlog(ctx, ping=None):
    if Permissions.check_no_permissions(ctx.author): return
    await ReactionActions.event_leaderboard(bot, ctx, ping)

@bot.command(name='updatestats')
async def update_stats(ctx):
    await Stats.update(ctx)

@bot.event
async def on_message(message):
    if message.channel.id == About.IGNORED_CHANNEL_ID: return
    if message.author == bot.user: return
    await Polls.check_reply(bot, message)
    if Permissions.check_no_admin_permissions(message.author) == False: 
        await bot.process_commands(message) # Needed to allow other commands to work
    else:
        await Censoring.check_censor(bot, message)
        await bot.process_commands(message) # Needed to allow other commands to work

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
    Stats.update_server_member_data(member.guild)
    await Moderation.give_member_role(member)
    log_channel = Utilities.get_modlog_channel(bot)
    embed_log = discord.Embed(title=f"Member joined", description=f"{member.mention} ({member.id})", color=0x5ea4ff)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    await log_channel.send(embed=embed_log)

@bot.event
async def on_member_remove(member):
    Stats.update_server_member_data(member.guild)
    log_channel = Utilities.get_modlog_channel(bot)
    embed_log = discord.Embed(title=f"Member left", description=f"{member.mention} ({member.id})", color=0x995eff)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    await log_channel.send(embed=embed_log)


@bot.event
async def on_ready():
    print(f"Ready - {About.INFO}!")
    asyncio.create_task(TimedActions.check_timed_actions(bot))
    asyncio.create_task(Help.clean_up_helps())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You need a higher role ;-;')


bot.run(TOKEN)


