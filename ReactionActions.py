import Reactions
import Permissions
import FileContents
import Utilities
import Help
import discord

PROGRESS_EMOJI_ID = 863079541675917402

def read_reaction_line(line):
    components = line.strip().split(":", 2) # address : emoji ID : action
    address_components = components[0].split("/")
    value_split = components[1].split(",")

    server_id = int(address_components[0])
    channel_id = int(address_components[1])
    message_id = int(address_components[2])

    emoji_id = value_split[0]
    action = value_split[1]

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

def save_reaction_action(server_id, channel_id, message_id, emoji_id, action, filename = 'Output/ReactionActions.txt'):
    message_address = f"{server_id}/{channel_id}/{message_id}"
    value = f"{emoji_id},{action}"
    keyvalue = f"{message_address}:{value}"

    Utilities.append_to_file(filename, keyvalue)

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
                if reacted_emoji.name == "Plus1":
                    current_value = Utilities.read_value_from_file('Output/Events.txt', str(message_user_id))
                    if current_value:
                        number = int(current_value) + 1
                        Utilities.save_key_value_to_file('Output/Events.txt', str(message_user_id), str(number))
                    else:
                        Utilities.save_key_value_to_file('Output/Events.txt', str(message_user_id), "1")

                with open('Output/Output.txt', 'a') as file:
                    string = f"{message.jump_url}\n"
                    file.write(string)
            else:
                if reacted_emoji.name == "Plus1":
                    current_value = Utilities.read_value_from_file('Output/Events.txt', str(message_user_id))
                    if current_value:
                        number = int(current_value) - 1
                        Utilities.save_key_value_to_file('Output/Events.txt', str(message_user_id), str(number))

    async def read_file(file):
        file_contents = FileContents.get_file_contents(file)
        for line in file_contents:
            user_id = str(payload.user_id)
            action = read_reaction_line(line)
            if reacted_message_id == action.message_id:
                if str(reacted_emoji.id) == action.emoji_id:
                    await perform_reaction_action(bot, user_id, action.server_id, action.channel_id, action.message_id, action.emoji_id, action.action, add_instructions)

    with open("Output/PermanentReactionActions.txt", 'r') as file:
        await read_file(file)

    with open("Output/ReactionActions.txt", 'r') as file:
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
    # elif "help." in action_string:
    #     action_split = action_string.split(".")
    #     topic_id = int(action_split[1].strip())
    #     session_user_id = int(action_split[2].strip())

    #     if session_user_id == int(user_id):
    #         cleanup_message_reactions(server_id, channel_id, message_id)
    #         await Help.continue_help(bot, server, channel, message, topic_id, session_user_id, emoji_id)
    #     else:
    #         if extra_instructions == "add":
    #             progress_reaction = Utilities.get_emoji_from_id(bot, PROGRESS_EMOJI_ID)
    #             await message.add_reaction(progress_reaction)

    #             for reaction in message.reactions:
    #                 if reaction.emoji.id == int(emoji_id):
    #                     users = await reaction.users().flatten()
    #                     for user in users:
    #                         is_bot = Permissions.check_is_bot(user)
    #                         is_session_user = session_user_id == user.id
    #                         if is_bot == False and is_session_user == False:
    #                             await message.remove_reaction(reaction, user)
    #             await message.remove_reaction(progress_reaction, bot.user)


def cleanup_message_reactions(server_id, channel_id, message_id):
    message_address = f"{server_id}/{channel_id}/{message_id}"
    new_file_contents = []
    with open('Output/ReactionActions.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
        
        for line in file_contents:
            if message_address not in line:
                new_file_contents.append(line)

    with open('Output/ReactionActions.txt', 'w') as file:
        combined = FileContents.combine_file_contents(new_file_contents)
        file.write(combined)

def cleanup_reaction_action(server_id, channel_id, message_id, emoji_id, action_string):
    message_address = f"{server_id}/{channel_id}/{message_id}"
    string = f"{message_address}:{emoji_id}:{action_string}"

    with open('Output/ReactionActions.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        for line in file_contents:
            if string in line:
                file_contents.remove(line)
    
    with open('Output/ReactionActions.txt', 'w') as file:
        combined = FileContents.combine_file_contents(file_contents)
        file.write(combined)