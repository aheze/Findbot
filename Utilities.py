import FileContents

import discord
import random
import asyncio

async def get_message_from_url(bot, url):
    link = url.split('/')

    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])

    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    return message

# get an emoji by name
def get_emoji(bot, name):
    emoji = None
    for guild in bot.guilds:
        found_emoji = discord.utils.get(guild.emojis, name=name)

        if found_emoji:
            emoji = found_emoji
            break

    return emoji

def get_emoji_from_id(bot, id):
    emoji = None
    for guild in bot.guilds:
        found_emoji = discord.utils.get(guild.emojis, id=id)

        if found_emoji:
            emoji = found_emoji
            break

    return emoji

def get_modlog_channel(bot):
    with open('Output/ServerConfig.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        for line in file_contents:
            if "modlog:" in line:
                line_split = line.split(":")
                server_id = int(line_split[1])
                channel_id = int(line_split[2])

                log_server = bot.get_guild(server_id)
                log_channel = log_server.get_channel(channel_id)
                return log_channel

def random_message(type, user_mention = None):
    categories = []
    with open('Config/RandomMessage.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)


        # 0: rate
        # 1: How to rate the app
        # 2: First, open...
        # 3: Then......
        current_category = []
        for line in file_contents:
            content_line = line
            if line.startswith("{"):
                current_category = []
                categories.append(current_category)
                
                raw_line_name = line.removeprefix("{").strip()
                category_name = raw_line_name.split("}", 1)[0]
                current_category.append(category_name)
            else:
                current_category.append(content_line)

    for category in categories:
        if type in category[0]:
            message = random.choice(category[1:])
            message_string = message

            if user_mention:
                message_string = message_string.replace("<m>", user_mention)

            return message_string


def readable_list(list) -> str:
    # Ref: https://stackoverflow.com/a/53981846/
    list = [str(s) for s in list]
    if len(list) < 3:
        return ' and '.join(list)
    return ', '.join(list[:-1]) + ', and ' + list[-1]