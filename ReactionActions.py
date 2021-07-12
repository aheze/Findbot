from Reactions import react
import Permissions
import FileContents
import Utilities
import Help
import discord

PROGRESS_EMOJI_ID = 863079541675917402

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

async def determine_reaction_action(bot, payload, add_instructions):

    reacted_message_id = payload.message_id
    reacted_emoji = payload.emoji

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
        print("claim!")
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
            await Help.continue_help(bot, server, channel, message, topic_id, session_user_id)
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