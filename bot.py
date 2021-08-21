
# bot.py - test

from logging import error
import os
from asyncio.base_events import Server
import discord

from discord.ext import commands
from discord.ext import tasks
import typing


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
import Events
import Stories
import MultiServer

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUIDE_TOKEN = os.getenv('GUIDE_DISCORD_TOKEN') 

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
intents.messages = True
intents.voice_states = True
intents.invites = True

activity = discord.Game(name="getfind.app")
bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    z_About.PREFIX), activity=activity, intents=intents, help_command=None)

guide_client = discord.Client()


# Emoji
RED = "<:Red:860713765107400714>"
GREEN = "<:Green:860713764742496258>"
RED_ID = "860713765107400714"
GREEN_ID = "860713764742496258"

# IDs
FINDBOT_ID = "784531493204262942"
FINDBOT_TEST_ID = "860667927345496075"

@bot.command(name="deleteallemojis")
async def delete_all_emojis(ctx):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await ctx.send("Type `yes` to confirm deleting all emoji from this server.")
    def check(m):
        return m.content == 'yes' and m.channel == ctx.channel

    msg = await bot.wait_for('message', timeout=10.0, check=check)
    if msg:
        deleting_message = await ctx.send("Confirmed. Deleting...")
        emojis_count = len(ctx.guild.emojis)
        for index, emoji in enumerate(ctx.guild.emojis):
            await emoji.delete()

            if index == emojis_count - 1:
                await deleting_message.edit(f"Finished deleting.")
            else:
                await deleting_message.edit(f"Confirmed. Deleting ({index + 1}/{emojis_count})")
    else:
        await ctx.send("Cancelled.")



@bot.command(name='ping')
async def ping(ctx):
    await Misc.ping(bot, ctx)


@bot.command(name='dance')
async def dance(ctx):
    await Misc.dance(ctx)


@bot.command(name='pfp')
async def get_pfp(ctx, user: discord.User):
    await Misc.get_pfp(ctx, user)


@bot.command(name='help')
async def help(ctx, *args):
    await Help.help(bot, ctx, args)


@bot.command(name='embed')
async def make_embed(ctx):
    embed = discord.Embed(description="<a:Typing_1:875550250155274290><a:Typing_2:875550249190559754><a:Typing_3:875550249702289408>", color=0x2f3136)
    await ctx.send(embed=embed)


@bot.command(name='story')
async def story(ctx, *args):
    await Stories.choose_story(bot, guide_client, ctx)

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


@bot.command(name='config')
async def configurate(ctx, name, value: typing.Union[discord.TextChannel, discord.User]):
    if Permissions.check_no_admin_permissions(ctx.author): return
    await Config.configurate(ctx, name, value)

@bot.group()
async def event(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Event [under construction]')

@event.command()
async def leaderboard(ctx, ping=None):
    if Permissions.check_no_permissions(ctx.author): return
    await Events.send_leaderboard(bot, ctx, ping)

@event.command()
async def new(ctx):
    if Permissions.check_no_permissions(ctx.author): return
    await Events.make_new_event(bot, ctx)


@bot.command(name='updatestats')
async def update_stats(ctx):
    await Stats.update(ctx)

@bot.event
async def on_message(message):
    if message.channel.id == z_About.IGNORED_CHANNEL_ID: return
    if message.author == bot.user: return

    await Polls.check_reply(message)
    await Events.check_reply(message)

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
    print(discord.version_info)
    asyncio.create_task(TimedActions.check_timed_actions(bot))
    update_guild_stats.start()

@tasks.loop(hours=2)
async def update_guild_stats():
    guild = bot.get_guild(807790675998277672)
    Stats.update_server_stats(guild)

@update_guild_stats.before_loop
async def before_loop():
    await bot.wait_until_ready()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You need a higher role ;-;')

@guide_client.event
async def on_ready():
    print(f'{guide_client.user} has connected to Discord!')
    # MultiServer.setup_new_server(bot, bot.get_guild(807790675998277672))

@bot.command(name='setup')
async def setup_new_server(ctx):
    if Permissions.check_no_admin_permissions(ctx.author): return
    MultiServer.setup_new_server(bot, ctx.guild)
    await ctx.message.add_reaction(GREEN)

@bot.command(name='settings')
async def setup_new_server(ctx):
    if Permissions.check_no_admin_permissions(ctx.author): return
    MultiServer.setup_new_server(bot, ctx.guild)
    await ctx.message.add_reaction(GREEN)

# @bot.event
# async def on_guild_join(guild):

    # general = find(lambda x: x.name == 'general',  guild.text_channels)
    # if general and general.permissions_for(guild.me).send_messages:
    #     await general.send('Hello {}!'.format(guild.name))



loop = asyncio.get_event_loop()
loop.create_task(bot.start(TOKEN))
loop.create_task(guide_client.start(GUIDE_TOKEN))
loop.run_forever()
