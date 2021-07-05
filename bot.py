# bot.py - test
# version 1

from logging import error
from datetime import datetime, timedelta
import os
import discord
import asyncio

from discord.ext import commands
from dotenv import load_dotenv

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

# Role IDs
MOD_ID = "859636240978673715"
ADMIN_ID = "743230678795288637"
MUTED_ID = 861271876185751553

# File actions
TIME_FORMATTING = "%m.%d.%Y.%H.%M.%S"

with open('BadWords.txt', 'r') as f:
    global badwords  # You want to be able to access this throughout the code
    badwords = f.read().splitlines()

# get an emoji by name
def get_emoji(name):
    emoji = None
    for guild in bot.guilds:
        found_emoji = discord.utils.get(guild.emojis, name=name)

        if found_emoji:
            emoji = found_emoji
            break

    return emoji

def check_no_permissions(author):
    role_ids = [str(role.id) for role in author.roles]
    return MOD_ID not in role_ids and str(author.id) != ADMIN_ID

def check_no_admin_permissions(author):
    role_ids = [str(role.id) for role in author.roles]
    return str(author.id) != ADMIN_ID

@bot.command(name='ping')
async def ping(ctx):
    await ctx.message.reply("pong")

@bot.command(name='pfp')
async def get_pfp(ctx, user: discord.User):
    user_pfp_link = user.avatar_url
    embed = discord.Embed(description=f"{user.name}'s profile pic:", color=0xe8ba00)
    embed.set_image(url=user_pfp_link)
    await ctx.send(embed=embed)


@bot.command(name='unmute')
async def unmute(ctx, user: discord.User, reason = ""):
    print("unmute!")
    if check_no_permissions(ctx.author): return
    server = ctx.guild
    member = server.get_member(user.id)
    muted_role = discord.utils.get(server.roles, id=MUTED_ID)
    await member.remove_roles(muted_role)

    keywords = ["unmute", str(user.id)]
    remove_timed_actions(keywords)
    embed = discord.Embed(description=f"Unmuted {member.mention}", color=0x1ce800)
    await ctx.send(embed=embed)

    log_channel = get_modlog_channel()
    embed_log = discord.Embed(title="Unmuted", color=0x1ce800)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    embed_log.add_field(name="Unmuter:", value=f"{ctx.author.mention} ({ctx.author.id})", inline=True)
    embed_log.add_field(name="Unmuted:", value=f"{member.mention} ({member.id})", inline=True)

    await log_channel.send(embed=embed_log)


@bot.command(name='mute')
async def mute(ctx, user: discord.User, *args):
    print("mute!")
    if check_no_permissions(ctx.author): return

    if args:
        first_arg = args[0]
        if first_arg[0].isalpha():
            time = "3"
            reason = " ".join(args)
        else:
            time = first_arg
            reason = " ".join(args[1:])
    else:
        print("no args")
        time = "3"
        reason = ""

    delay_time = datetime.now()
    allowed_extensions = ("s", "m", "h", "d")
    if time.endswith(allowed_extensions):

        time_int = int(time[:-1])
        last_character = time[-1]
        if last_character == "s":
            delay_time += timedelta(seconds=time_int)
            length_string = f"{time_int} seconds"
        elif last_character == "m":
            delay_time += timedelta(minutes=time_int)
            length_string = f"{time_int} minutes"
        elif last_character == "h":
            delay_time += timedelta(hours=time_int)
            length_string = f"{time_int} hours"
        else:
            delay_time += timedelta(days=time_int)
            length_string = f"{time_int} days"
            
    elif time[-1].isalpha():
        time_int = int(time[:-1])
        delay_time += timedelta(seconds=time_int)
        length_string = f"{time_int} seconds"
    else: # just int, so seconds
        time_int = int(time)
        delay_time += timedelta(minutes=time_int)
        length_string = f"{time_int} minutes"
    
    server = ctx.guild
    member = server.get_member(user.id)
    muted_role = discord.utils.get(server.roles, id=MUTED_ID)
    action_string = f"unmute.{ctx.guild.id}.{user.id}"
    await member.add_roles(muted_role)

    print("action:")
    print(action_string)

    keywords = ["unmute", str(user.id)]
    remove_timed_actions(keywords)
    remove_timed_actions(action_string)
    save_timed_action(delay_time, action_string)

    embed = discord.Embed(description=f"Muted {member.mention} for {length_string}", color=0xe8fc03)
    
    if reason:
        reason_string = f"Reason: {reason}"
    else:
        reason_string = "No reason given"
    embed.set_footer(text=reason_string)

    await ctx.send(embed=embed)

    log_channel = get_modlog_channel()
    embed_log = discord.Embed(title=f"Muted for {length_string}", color=0xe8fc03)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    embed_log.add_field(name="Muter:", value=f"{ctx.author.mention} ({ctx.author.id})", inline=True)
    embed_log.add_field(name="Muted:", value=f"{member.mention} ({member.id})", inline=True)
    embed_log.set_footer(text=reason_string)
    await log_channel.send(embed=embed_log)

# remove
def remove_timed_actions(keywords):
    print("removing action")
    new_file_contents = []
    with open('z_TimedActions.txt', 'r') as file:
        file_contents = get_file_contents(file)
        
        for line in file_contents:
            components = line.strip().split(":") # 0 is time, 1 is action
            if not any(word in components[1] for word in keywords):
                new_file_contents.append(line)

    with open('z_TimedActions.txt', 'w') as file:
        combined = combine_file_contents(new_file_contents)
        file.write(combined)

def save_timed_action(time, action):
    delay_time_string = time.strftime(TIME_FORMATTING)
    with open('z_TimedActions.txt', 'a') as file:
        string = f"{delay_time_string}:{action}\n"
        file.write(string)

def get_modlog_channel():
    with open('z_ServerConfig.txt', 'r') as file:
        file_contents = get_file_contents(file)

        for line in file_contents:
            if "modlog:" in line:
                line_split = line.split(":")
                server_id = int(line_split[1])
                channel_id = int(line_split[2])

                log_server = bot.get_guild(server_id)
                log_channel = log_server.get_channel(channel_id)
                return log_channel

@bot.command(name='react')
async def react(ctx, message_id, reaction):
    if check_no_permissions(ctx.author): return
    message = await ctx.fetch_message(message_id)
    emoji = get_emoji(reaction)
    if emoji:
        await message.add_reaction(emoji)
    else:
        await ctx.message.reply(f"`{reaction}` emoji was not found")

@bot.command(name='clearreacts')
async def set_reaction_roles(ctx, message_link):
    if check_no_permissions(ctx.author): return
    link = message_link.split('/')

    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])

    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    await message.clear_reactions()



@bot.command(name='reactroles')
async def set_reaction_roles(ctx, message_link, *reaction_roles):
    if check_no_admin_permissions(ctx.author): return

    print("set reaction roles!")
    link = message_link.split('/')
    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])
    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    emoji_not_founds = []
    role_not_founds = []
    duplicate_roles_messages = []

    # message address : emoji ID : action (assign role)
    for reaction_role in reaction_roles:
        emoji_to_role = reaction_role.split(":")
        emoji = get_emoji(emoji_to_role[0])

        if emoji:
            role = discord.utils.get(server.roles, name=emoji_to_role[1])
            if role:
                role_id = role.id
                has_error = save_reaction_action(server_id, channel_id, message_id, emoji.id, f"role.{role_id}", "z_PermanentReactionActions.txt")
                if has_error:
                    message = f"`{emoji.name}` emoji is already assigned to `{role.name}` role"
                    duplicate_roles_messages.append(message)
                else:
                    await message.add_reaction(emoji)
            else:
                role_not_founds.append(emoji_to_role[1])
        else:
            emoji_not_founds.append(emoji_to_role[0])

    if not emoji_not_founds and not role_not_founds and not duplicate_roles_messages:
        await ctx.message.add_reaction(GREEN)
    else:
        await ctx.message.add_reaction(RED)

    if emoji_not_founds:
        error_message = ""
        for emoji in emoji_not_founds:
            error = f"Emoji not found: {emoji}\n"
            error_message += error
        await ctx.message.reply(error_message)


    if role_not_founds:
        error_message = ""
        for role in role_not_founds:
            error = f"Role not found: {role}\n"
            error_message += error
        await ctx.message.reply(error_message)

    if duplicate_roles_messages:
        duplicate_roles_message = "\n".join(duplicate_roles_messages)
        await ctx.message.reply(duplicate_roles_message)


@bot.command(name='setmodlog')
async def set_modlog(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    channel_id = str(channel.id)
    string = f'modlog:{guild_id}:{channel_id}\n'

    line_overridden = False
    with open('z_ServerConfig.txt', 'r') as file:
        file_contents = get_file_contents(file)
                
        for index, line in enumerate(file_contents):
            if "modlog:" in line:
                file_contents[index] = string
                line_overridden = True
                break

    if line_overridden == False:
        with open('z_ServerConfig.txt', 'a') as file:
            file.write(string)
    else:
        with open('z_ServerConfig.txt', 'w') as file:
            combined = combine_file_contents(file_contents)
            file.write(combined)

    await ctx.message.add_reaction(GREEN)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content.split()

    bad_word = ""
    for word in badwords:
        if word.lower() in msg:
            print(f"Bad word: {word}, in {msg}")
            bad_word = word
            break
    
    if bad_word != "":
        channel = message.channel

        embed = discord.Embed(description=f"{message.author.mention}, don't say that >:(", color=0xFF0000)
        embed.set_footer(text=f"React with the check to dismiss")

        await message.delete()
        warning_message = await channel.send(embed=embed)
        warning_channel = warning_message.channel
        warning_server = warning_channel.guild

        save_reaction_action(warning_server.id, warning_channel.id, warning_message.id, GREEN_ID, "delete")
        await warning_message.add_reaction(GREEN)

        with open('z_ServerConfig.txt', 'r') as file:
            file_contents = get_file_contents(file)

            for line in file_contents:
                if "modlog:" in line:
                    line_split = line.split(":")
                    server_id = int(line_split[1])
                    channel_id = int(line_split[2])

                    log_server = bot.get_guild(server_id)
                    log_channel = log_server.get_channel(channel_id)

                    embed_log = discord.Embed(title="Censored Message:", description=f"{message.content}", color=0xFF0000)
                    embed_log.set_author(name=message.author.display_name, url=f"https://discord.com/users/{message.author.id}", icon_url=message.author.avatar_url)
                    embed_log.add_field(name="User details", value=f"{message.author.mention} ({message.author.id})", inline=False)
                    embed_log.set_footer(text=f"Censored word: {bad_word}")
                    await log_channel.send(embed=embed_log)
                    break

    await bot.process_commands(message) # Needed to allow other commands to work

@bot.event
async def on_raw_reaction_add(payload):
    if str(payload.user_id) == FINDBOT_TEST_ID or str(payload.user_id) == FINDBOT_ID:
        return
    await determine_reaction_action(payload, "add")

@bot.event
async def on_raw_reaction_remove(payload):
    if str(payload.user_id) == FINDBOT_TEST_ID or str(payload.user_id) == FINDBOT_ID:
        return
    await determine_reaction_action(payload, "remove")


def save_reaction_action(server_id, channel_id, message_id, emoji_id, action, filename = "z_ReactionActions.txt"):

    message_address = f"{server_id}/{channel_id}/{message_id}"
    with open(filename, 'r+') as file:
        file_contents = get_file_contents(file)

        duplicate_lines = []
        for line in file_contents:
            if message_address in line:
                if str(emoji_id) in line:
                    duplicate_lines.append(line)
                    break

    if duplicate_lines:
        print("Reaction action has errors in these lines:")
        print(duplicate_lines)
        with open('z_Errors.log', 'a') as file:
            file.write(f'Reaction action has errors in these lines: {duplicate_lines}\n')

        return True # has error
    else:
        with open(filename, 'a') as file:
            string = f"{message_address}:{emoji_id}:{action}\n"
            file.write(string)
            

def read_reaction_line(line):
    components = line.strip().split(":") # address : emoji ID : action
    address_components = components[0].split("/")

    server_id = int(address_components[0])
    channel_id = int(address_components[1])
    message_id = int(address_components[2])
    emoji_id = components[1]
    action = components[2]

    return ReactionAction(
        server_id,
        channel_id,
        message_id,
        emoji_id,
        action
    )

class ReactionAction:
    def __init__(self, server_id, channel_id, message_id, emoji_id, action):
        self.server_id = server_id
        self.channel_id = channel_id
        self.message_id = message_id 
        self.emoji_id = emoji_id 
        self.action = action

async def determine_reaction_action(payload, add_instructions):

    reacted_message_id = payload.message_id
    reacted_emoji = payload.emoji

    async def read_file(file):
        file_contents = get_file_contents(file)

        for line in file_contents:
            user_id = str(payload.user_id)

            action = read_reaction_line(line)

            if reacted_message_id == action.message_id:
                if str(reacted_emoji.id) == action.emoji_id:
                    await perform_action(user_id, action.server_id, action.channel_id, action.message_id, action.emoji_id, action.action, add_instructions)

    with open("z_PermanentReactionActions.txt", 'r') as file:
        await read_file(file)

    with open("z_ReactionActions.txt", 'r') as file:
        await read_file(file)


async def perform_action(user_id, server_id, channel_id, message_id, emoji_id, action_string, extra_instructions = ""):
    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    if action_string == "delete":
        await message.delete()
        cleanup_reaction_action(server_id, channel_id, message_id, emoji_id, action_string)
    elif "role." in action_string:

        action_split = action_string.split(".")
        role_id = int(action_split[1].strip()) # must be int
        role = discord.utils.get(server.roles, id=role_id)
        member = server.get_member(int(user_id))

        if extra_instructions:
            if extra_instructions == "add":
                await member.add_roles(role)
            else:
                await member.remove_roles(role)
        else:
            if role in member.roles:
                await member.remove_roles(role)
            else:
                await member.add_roles(role)

def cleanup_reaction_action(server_id, channel_id, message_id, emoji_id, action_string):
    message_address = f"{server_id}/{channel_id}/{message_id}"
    string = f"{message_address}:{emoji_id}:{action_string}"

    with open('z_ReactionActions.txt', 'r') as file:
        file_contents = get_file_contents(file)

        for line in file_contents:
            if string in line:
                file_contents.remove(line)
    
    with open('z_ReactionActions.txt', 'w') as file:
        combined = combine_file_contents(file_contents)
        file.write(combined)

def get_file_contents(file):
    raw_lines = list(filter(None, file.readlines()))
    file_contents = [x.rstrip() for x in raw_lines if x.rstrip()]
    return file_contents

# combine into a single str
def combine_file_contents(file_contents):
    combined = "\n".join(file_contents)
    combined += "\n"
    if combined == "\n":
        combined = ""
    return combined

async def check_timed_actions():
    while True:
        new_file_contents = []
        with open('z_TimedActions.txt', 'r') as file:
            file_contents = get_file_contents(file)
            
            for line in file_contents:
                components = line.strip().split(":") # 0 is time, 1 is action
                time = datetime.strptime(components[0], TIME_FORMATTING)
                if datetime.now() > time: # execute action, delete line
                    action_string = components[1]
                    action_split = action_string.split(".")
                    server_id = int(action_split[1].strip())
                    user_id = int(action_split[2].strip())

                    if "unmute." in action_string:
                        server = bot.get_guild(server_id)
                        member = server.get_member(user_id)
                        muted_role = discord.utils.get(server.roles, id=MUTED_ID)
                        print(f"Unmuting {member}")
                        print(muted_role)
                        await member.remove_roles(muted_role)
                else:
                    new_file_contents.append(line)
        with open('z_TimedActions.txt', 'w') as file:
            combined = combine_file_contents(new_file_contents)
            file.write(combined)


        await asyncio.sleep(5)

@bot.event
async def on_ready():
    print("Ready to test!")
    await check_timed_actions()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You need a higher role ;-;')


bot.run(TOKEN)


