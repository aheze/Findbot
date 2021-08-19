import FileContents

import discord
import random
import os

def append_to_file(file, keyvalue):
    with open(file, 'a') as f:
        string = keyvalue + "\n"
        f.write(string)

def save_key_value_to_file(file, key, value):
    line_overridden = False
    with open(file, 'r') as f:
        file_contents = FileContents.get_file_contents(f)
                
        for index, line in enumerate(file_contents):
            if key in line:
                file_contents[index] = f"{key}:{value}"
                line_overridden = True
                break

    if not line_overridden:
        file_contents.append(f"{key}:{value}")

    with open(file, 'w') as f:
        combined = FileContents.combine_file_contents(file_contents)
        f.write(combined)

def read_value_from_file(file, keyword):
    with open(file, 'r') as f:
        file_contents = FileContents.get_file_contents(f)
        for line in file_contents:
            if keyword in line:
                line_split = line.split(":", 1)
                return line_split[1]

def check_existing_in_file(file, keyword):
    with open(file, 'r') as f:
        file_contents = FileContents.get_file_contents(f)
        for line in file_contents:
            if keyword in line:
                return line



async def get_message_from_url(bot, url):
    link = url.split('/')

    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])

    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    return message

def get_specific_emoji(bot, server_ids, emoji_name):
    for server_id in server_ids:
        server = bot.get_guild(server_id)
        found_emoji = discord.utils.get(server.emojis, name=emoji_name)
        if found_emoji:
            return found_emoji

# get an emoji by name
def get_emoji(bot, name):
    emoji = None
    for guild in bot.guilds:
        found_emoji = discord.utils.get(guild.emojis, name=name)

        if found_emoji:
            emoji = found_emoji
            break

    return emoji

def get_specific_emoji_from_id(bot, server_ids, emoji_id):
    for server_id in server_ids:
        server = bot.get_guild(server_id)
        found_emoji = discord.utils.get(server.emojis, id=emoji_id)
        if found_emoji:
            return found_emoji

def get_emoji_from_id(bot, id):
    emoji = None
    for guild in bot.guilds:
        found_emoji = discord.utils.get(guild.emojis, id=id)

        if found_emoji:
            emoji = found_emoji
            break

    return emoji

def random_message(type, guild_id, user_mention = None):
    categories = []

    random_message_file = FileContents.server_path(guild_id, "Config/RandomMessage.txt")
    with open(random_message_file, 'r') as file:
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


def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path