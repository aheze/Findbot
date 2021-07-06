import FileContents

import discord
import asyncio

# get an emoji by name
def get_emoji(bot, name):
    emoji = None
    for guild in bot.guilds:
        found_emoji = discord.utils.get(guild.emojis, name=name)

        if found_emoji:
            emoji = found_emoji
            break

    return emoji

def get_modlog_channel(bot):
    with open('z_ServerConfig.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        for line in file_contents:
            if "modlog:" in line:
                line_split = line.split(":")
                server_id = int(line_split[1])
                channel_id = int(line_split[2])

                log_server = bot.get_guild(server_id)
                log_channel = log_server.get_channel(channel_id)
                return log_channel