import Reactions
import Permissions
import FileContents
import Utilities
import Help
import discord

PROGRESS_EMOJI_ID = 863079541675917402
EVENT_NAME = "Funcing destroy the bot"
EVENT_DESCRIPTION = "Exploit <@784531493204262942>'s censoring loopholes: **get 1 point** for every should-be-censored word or false positive! Spam test words in <#864710025460187156>. Challenge ends July 15th, 11:59 PM PST."
EVENT_FOOTER = 'Be at the top to get the "Beta Tester" role!'

def read_reaction_line(line):
    components = line.strip().split(":", 2) # address : emoji ID : action
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

def save_reaction_action(server_id, channel_id, message_id, emoji_id, action, filename = "z_ReactionActions.txt"):

    message_address = f"{server_id}/{channel_id}/{message_id}"
    with open(filename, 'r+') as file:
        file_contents = FileContents.get_file_contents(file)

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

def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1

async def event_leaderboard(bot, ctx, ping = None):
    with open("z_Events.txt", 'r') as file:

        leaderboard = []
        file_contents = FileContents.get_file_contents(file)
        for line in file_contents:
            line_split = line.split(":")
            user_id = int(line_split[0])
            user = bot.get_user(user_id)
            number = int(line_split[1])

            tuple = (user, number)
            leaderboard.append(tuple)

        leaderboard.sort(key=lambda tup: tup[1], reverse=True)  # sorts in place

        leaderboard_description = ""
        for (index, tuple) in enumerate(leaderboard):
            user = tuple[0]
            points = tuple[1]

            starting_trophy = ""
            if index == 0:
                starting_trophy = Utilities.get_emoji(bot, "First")
            elif index == 1:
                starting_trophy = Utilities.get_emoji(bot, "Second")
            elif index == 2:
                starting_trophy = Utilities.get_emoji(bot, "Third")
            else:
                starting_trophy = Utilities.get_emoji(bot, "NotSelected")

            new_line = ""
            if points == 1:
                new_line += f"{starting_trophy} {points} point: "
            else:
                new_line += f"{starting_trophy} {points} points: "

            if ping:
                new_line += f"{user.mention}\n"
            else:
                new_line += f"**{user.name}**\n"

            leaderboard_description += new_line

        description_start = EVENT_DESCRIPTION
        description = f"{description_start}\n\n{leaderboard_description}"

        channel = ctx.channel
        embed = discord.Embed(title=f'Leaderboard for the "{EVENT_NAME}" event!', description=description, color=0xebc334)
        embed.set_footer(text=EVENT_FOOTER)

        await channel.send(embed=embed)

async def determine_reaction_action(bot, payload, add_instructions):
    reacted_message_id = payload.message_id
    reacted_emoji = payload.emoji
    
    reaction_user_id = payload.user_id
    server = bot.get_guild(payload.guild_id)
    reaction_member = server.get_member(reaction_user_id)
    
    if not Permissions.check_no_permissions(reaction_member):
        if reacted_emoji.name == "Plus1" or reacted_emoji.name == "Finder":
            channel = server.get_channel(payload.channel_id)
            message = await channel.fetch_message(reacted_message_id)
            message_user_id = message.author.id

            if add_instructions == "add":
                new_file_contents = []
                with open("z_Events.txt", 'r') as file:
                    file_contents = FileContents.get_file_contents(file)
                    new_file_contents = file_contents

                    matching_user_index = index_containing_substring(file_contents, str(message_user_id))
                    if matching_user_index == -1:
                        new_file_contents.append(f"{message_user_id}:1")
                    else:
                        line = new_file_contents[matching_user_index]
                        line_split = line.split(":")
                        number = int(line_split[1])
                        if reacted_emoji.name == "Plus1":
                            number += 1
                        else:
                            number += 3
                        combined = f"{message_user_id}:{number}"
                        new_file_contents[matching_user_index] = combined

                with open("z_Events.txt", 'w') as file:
                    combined = FileContents.combine_file_contents(new_file_contents)
                    file.write(combined)

                with open('z_Output.txt', 'a') as file:
                    string = f"{message.jump_url}\n"
                    file.write(string)
            else:
                new_file_contents = []
                with open("z_Events.txt", 'r') as file:
                    file_contents = FileContents.get_file_contents(file)
                    new_file_contents = file_contents

                    matching_user_index = index_containing_substring(file_contents, str(message_user_id))
                    if matching_user_index != -1:
                        line = new_file_contents[matching_user_index]
                        line_split = line.split(":")
                        number = int(line_split[1])
                        if reacted_emoji.name == "Plus1":
                            number -= 1
                        else:
                            number -= 3
                        combined = f"{message_user_id}:{number}"
                        new_file_contents[matching_user_index] = combined

                with open("z_Events.txt", 'w') as file:
                    combined = FileContents.combine_file_contents(new_file_contents)
                    file.write(combined)

    async def read_file(file):
        file_contents = FileContents.get_file_contents(file)

        for line in file_contents:
            user_id = str(payload.user_id)

            action = read_reaction_line(line)

            if reacted_message_id == action.message_id:
                if str(reacted_emoji.id) == action.emoji_id:
                    await perform_reaction_action(bot, user_id, action.server_id, action.channel_id, action.message_id, action.emoji_id, action.action, add_instructions)

    with open("z_PermanentReactionActions.txt", 'r') as file:
        await read_file(file)

    with open("z_ReactionActions.txt", 'r') as file:
        await read_file(file)



async def perform_reaction_action(bot, user_id, server_id, channel_id, message_id, emoji_id, action_string, extra_instructions = ""):
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
    elif "claim." in action_string:
        action_split = action_string.split(".")
        claim_role_id = int(action_split[1].strip())
        claim_user_id = int(action_split[2])

        if claim_user_id == int(user_id):
            role = discord.utils.get(server.roles, id=claim_role_id)
            member = server.get_member(claim_user_id)

            if extra_instructions == "add":
                await member.add_roles(role)
            else:
                await member.remove_roles(role)
        else:
            if extra_instructions == "add":
                progress_reaction = Utilities.get_emoji_from_id(bot, PROGRESS_EMOJI_ID)
                await message.add_reaction(progress_reaction)

                for reaction in message.reactions:
                    if reaction.emoji.id == int(emoji_id):
                        users = await reaction.users().flatten()
                        for user in users:
                            is_bot = Permissions.check_is_bot(user)
                            is_awardee = claim_user_id == user.id
                            if is_bot == False and is_awardee == False:
                                await message.remove_reaction(reaction, user)

                await message.remove_reaction(progress_reaction, bot.user)
    elif "help." in action_string:
        action_split = action_string.split(".")
        topic_id = int(action_split[1].strip())
        session_user_id = int(action_split[2].strip())

        if session_user_id == int(user_id):
            cleanup_message_reactions(server_id, channel_id, message_id)
            await Help.continue_help(bot, server, channel, message, topic_id, session_user_id, emoji_id)
        else:
            if extra_instructions == "add":
                progress_reaction = Utilities.get_emoji_from_id(bot, PROGRESS_EMOJI_ID)
                await message.add_reaction(progress_reaction)

                for reaction in message.reactions:
                    if reaction.emoji.id == int(emoji_id):
                        users = await reaction.users().flatten()
                        for user in users:
                            is_bot = Permissions.check_is_bot(user)
                            is_session_user = session_user_id == user.id
                            if is_bot == False and is_session_user == False:
                                await message.remove_reaction(reaction, user)
                await message.remove_reaction(progress_reaction, bot.user)


def cleanup_message_reactions(server_id, channel_id, message_id):
    message_address = f"{server_id}/{channel_id}/{message_id}"
    new_file_contents = []
    with open('z_ReactionActions.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
        
        for line in file_contents:
            if message_address not in line:
                new_file_contents.append(line)

    with open('z_ReactionActions.txt', 'w') as file:
        combined = FileContents.combine_file_contents(new_file_contents)
        file.write(combined)

def cleanup_reaction_action(server_id, channel_id, message_id, emoji_id, action_string):
    message_address = f"{server_id}/{channel_id}/{message_id}"
    string = f"{message_address}:{emoji_id}:{action_string}"

    with open('z_ReactionActions.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        for line in file_contents:
            if string in line:
                file_contents.remove(line)
    
    with open('z_ReactionActions.txt', 'w') as file:
        combined = FileContents.combine_file_contents(file_contents)
        file.write(combined)