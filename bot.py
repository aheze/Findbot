# bot.py - test
# version 1

from logging import error
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix=',', intents=intents)

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



@bot.command(name='reactroles')
async def set_reaction_roles(ctx, message_link, *reaction_roles):
    print("set reaction roles!")
    link = message_link.split('/')
    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])
    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    # message address : emoji ID : action (assign role)

    for reaction_role in reaction_roles:
        emoji_to_role = reaction_role.split(":")
        emoji = await get_emoji(emoji_to_role[0])

        if emoji:
            save_reaction_action(server_id, channel_id, message_id, emoji.id, f"role.{emoji_to_role[1]}", "z_PermanentReactionActions.txt")
            await message.add_reaction(emoji)

    


    # print("action>")
    # print(reaction_actions)

    # for reaction_action in reaction_actions:


    #     z_PermanentReactionActions
    #     with open('z_ReactionRoles.txt', 'r+') as file:
    #         file_contents = file.readlines()

    #         matching = ""
    #         for line in file_contents:
    #             message_id = f'{tuple[0]}:'
    #             emoji = f'{tuple[1]}:'
    #             if message_id in line:
    #                 if emoji in line:
    #                     matching = tuple[2]

    #         # matching = [line.split(":")[1].strip() for line in file_contents if f'{tuple[0]}:' and f'{tuple[1]}:' in line] # get the matching roles
    #         print(f"matching: {matching}")

    #         if matching != "":
    #             print("Contains already") 
    #             full_error_message += f"`{tuple[1]}` emoji already assigned with `{matching}` role\n"
    #         else:
    #             string = f'{tuple[0]}:{tuple[1]}:{tuple[2]}\n'
    #             file.write(string)

    # if full_error_message == "":
    #     await ctx.message.add_reaction(GREEN)

    #     emoji_not_found = ""
    #     for tuple in arguments:
    #         emoji = await get_emoji(tuple[1])
    #         if emoji:
    #             await message.add_reaction(emoji)
    #         else:
    #             print(f"Emoji not found: {tuple[1]}")
    #             emoji_not_found += f"`{tuple[1]}` emoji not found\n"

    #     if emoji_not_found != "":
    #         await ctx.message.reply(emoji_not_found)
    # else:
    #     await ctx.message.add_reaction(RED)
        # await ctx.message.reply(full_error_message)


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
    await determine_reaction_action(payload)


def save_reaction_action(server_id, channel_id, message_id, emoji_id, action, filename = "z_ReactionActions.txt"):

    message_address = f"{server_id}/{channel_id}/{message_id}"
    with open(filename, 'r+') as file:
        file_contents = get_file_contents(file)

        matching_indices = []
        for index, line in enumerate(file_contents):
            if message_address in line:
                if str(emoji_id) in line:
                    matching_indices.append(index)
                    break

    if len(matching_indices) == 0:
        with open(filename, 'a') as file:
            string = f"{message_address}:{emoji_id}:{action}\n"
            file.write(string)
    else:
        print("Reaction action has errors in these lines:")
        print(matching_indices)
        with open('z_Errors.log', 'a') as file:
            file.write(f'Reaction action has errors in these lines: {matching_indices}\n')


async def determine_reaction_action(payload):

    reacted_message_id = payload.message_id
    reacted_emoji = payload.emoji

    async def read_file(file):
        file_contents = get_file_contents(file)

        for line in file_contents:
            components = line.strip().split(":") # address : emoji ID : action
            address_components = components[0].split("/")
            server_id = int(address_components[0])
            channel_id = int(address_components[1])
            message_id = int(address_components[2])

            emoji_id = components[1]
            action = components[2]

            if reacted_message_id == message_id:
                if str(reacted_emoji.id) == emoji_id:
                    await perform_action(server_id, channel_id, message_id, emoji_id, action)

    with open("z_PermanentReactionActions.txt", 'r') as file:
        await read_file(file)

    with open("z_ReactionActions.txt", 'r') as file:
        await read_file(file)


async def perform_action(server_id, channel_id, message_id, emoji_id, action_string):
    print("Performing react action")
    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    if action_string == "delete":
        await message.delete()
        cleanup_reaction_action(server_id, channel_id, message_id, emoji_id, action_string)
    elif "role." in action_string:
        print("role!!!!!!!")
        print(action_string)

def cleanup_reaction_action(server_id, channel_id, message_id, emoji_id, action_string):
    message_address = f"{server_id}/{channel_id}/{message_id}"
    string = f"{message_address}:{emoji_id}:{action_string}"

    with open('z_ReactionActions.txt', 'r') as file:
        file_contents = get_file_contents(file)

        for line in file_contents:
            if string in line:
                file_contents.remove(line)
    
    with open('z_ReactionActions.txt', 'w') as file:
        print("writing z_reactionactions")
        print(file_contents)
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
        print("combined was empty")
    return combined

@bot.event
async def on_ready():
    print("Ready to test!")


bot.run(TOKEN)