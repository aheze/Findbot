# bot.py
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)

# Emoji
RED = "<:Red:860713765107400714>"
GREEN = "<:Green:860713764742496258>"
RED_ID = "860713765107400714"
GREEN_ID = "860713764742496258"

# IDs
FINDBOT_ID = "784531493204262942"
FINDBOT_TEST_ID = "860667927345496075"

with open('BadWords.txt', 'r') as f:
    global badwords  # You want to be able to access this throughout the code
    badwords = f.read().splitlines()

# get an emoji by name
async def get_emoji(name):
    emoji = None
    for guild in bot.guilds:
        found_emoji = discord.utils.get(guild.emojis, name=name)

        if found_emoji:
            emoji = found_emoji
            break

    return emoji

@bot.command(name='react')
async def react(ctx, message_id, reaction):
    message = await ctx.fetch_message(message_id)
    emoji = await get_emoji(reaction)
    print(emoji)
    if emoji:
        await message.add_reaction(emoji)
    else:
        await ctx.message.reply(f"`{reaction}` emoji was not found")

@bot.command(name='clearreacts')
async def set_reaction_roles(ctx, message_link):
    link = message_link.split('/')

    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])

    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    await message.clear_reactions()


@bot.command(name='setmodlog')
async def set_modlog(ctx, channel: discord.TextChannel):
    print("--- set modlog")
    print(ctx.guild)
    print(channel.id)

    guild_id = str(ctx.guild.id)
    channel_id = str(channel.id)
    string = f'modlog:{guild_id}:{channel_id}\n'

    line_overridden = False
    with open('z_ServerConfig.txt', 'r') as file:
        file_contents = file.readlines()
        print("Old file contents")
        print(file_contents)
                
        for index, line in enumerate(file_contents):
            if "modlog:" in line:
                print("Exists already")
                print(line)
                file_contents[index] = string
                print("writing, new:")
                print(file_contents)
                line_overridden = True
                break

    if line_overridden == False:
        with open('z_ServerConfig.txt', 'a') as file:
            print(f"Writing: {string}")
            file.write(string)
    else:
        with open('z_ServerConfig.txt', 'w') as file:
            combined = "\n".join(file_contents)
            print("combined:")
            print(combined)
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
        print(message.author.id)

        channel = message.channel

        
        embed = discord.Embed(description=f"{message.author.mention}, don't say that >:(", color=0xFF0000)
        await message.delete()
        print("sending/....")
        warning_message = await channel.send(embed=embed)
        warning_channel = warning_message.channel
        warning_server = warning_channel.guild

        errors = save_reaction_action(warning_server.id, warning_channel.id, warning_message.id, GREEN_ID, "delete")
        await warning_message.add_reaction(GREEN)

        with open('z_ServerConfig.txt', 'r') as file:
            file_contents = list(filter(None, file.readlines()))
            print("File contents")
            print(file_contents)

            for line in file_contents:
                if "modlog:" in line:
                    line_split = line.split(":")
                    print(line_split)
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
        print("Bot added the reaction")
        return

    print("Reaction added")
    await determine_reaction_action(payload)

# Returns a list of the lines inside z_ReactionActions.txt that have an error
def save_reaction_action(server_id, channel_id, message_id, emoji_id, action):
    print("save reaction")

    message_address = f"{server_id}/{channel_id}/{message_id}"
    with open('z_ReactionActions.txt', 'r+') as file:
        file_contents = file.readlines()

        matching_indices = []
        for index, line in enumerate(file_contents):
            if message_address in line:
                if emoji_id in line:
                    matching_indices.append(index)
                    break

    if len(matching_indices) == 0:
        with open('z_ReactionActions.txt', 'a') as file:
            string = f"{message_address}:{emoji_id}:{action}\n"
            print(f"Writing: {string}")
            file.write(string)
    else:
        return matching_indices


async def determine_reaction_action(payload):

    reacted_message_id = payload.message_id
    reacted_emoji = payload.emoji

    print(reacted_emoji.id)
    # print(guild)

    with open('z_ReactionActions.txt', 'r') as file:
        file_contents = file.readlines()
        for line in file_contents:
            components = line.strip().split(":") # address : emoji ID : action
            address_components = components[0].split("/")
            server_id = int(address_components[0])
            channel_id = int(address_components[1])
            message_id = int(address_components[2])

            emoji_id = components[1]
            action = components[2]

            if reacted_message_id == message_id:
                print("same ID")
                if str(reacted_emoji.id) == emoji_id:
                    print("same emoji!!!!")
                    await perform_action(server_id, channel_id, message_id, emoji_id, action)


async def perform_action(server_id, channel_id, message_id, emoji_id, action_string):
    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    if action_string == "delete":
        await message.delete()
        cleanup_reaction_action(server_id, channel_id, message_id, emoji_id, action_string)

def cleanup_reaction_action(server_id, channel_id, message_id, emoji_id, action_string):
    message_address = f"{server_id}/{channel_id}/{message_id}"
    string = f"{message_address}:{emoji_id}:{action_string}\n"

    with open('z_ReactionActions.txt', 'r') as file:
        file_contents = list(filter(None, file.readlines()))

        for line in file_contents:
            if string in line:
                print("exists!!!")
                file_contents.remove(line)
    
    with open('z_ReactionActions.txt', 'w') as file:
        combined = "\n".join(file_contents)
        print("combined:")
        print(combined)
        file.write(combined)

@bot.event
async def on_ready():
    print("Ready to test!")


bot.run(TOKEN)