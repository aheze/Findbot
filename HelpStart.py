import Help
import Utilities
import ReactionActions
import uuid
from anytree import Node, RenderTree, search

current_help = None

# requires_perform_queued = False
queued_message = None
queued_server_id = None
queued_channel_id = None
queued_emoji_to_action = None

async def help(bot, ctx):
    await start_help(bot, ctx)

async def start_help(bot, ctx):
    topic_tree = Help.parse_tree()

    text, emoji_to_action = get_help_content(bot, "", ctx.author.id, topic_tree, topic_tree.name)
    message = await ctx.send(text)
    server = ctx.guild
    channel = message.channel
    await add_reactions(message, server.id, channel.id, emoji_to_action)

async def continue_help(bot, server, channel, message, id, session_user_id):
    global current_help 
    # global requires_perform_queued
    global queued_message
    global queued_server_id
    global queued_channel_id
    global queued_emoji_to_action

    existing_content = message.content
    existing_message_string = existing_content + "\n\n⇣\n\n"
    topic_tree = Help.parse_tree()
    node = search.find(topic_tree, lambda node: f"{id}<->" in node.name)
    node_name = Help.get_name_for(node)[2]

    text, emoji_to_action = get_help_content(bot, existing_message_string, session_user_id, node, node_name)
    edited_message = await message.edit(content=text)

    if current_help:
        print("ongoing...")
        # requires_perform_queued = True
        current_help = str(uuid.uuid4())
        queued_message = message
        queued_server_id = server.id
        queued_channel_id = channel.id
        queued_emoji_to_action = emoji_to_action
    else:
        await message.clear_reactions()
        await add_reactions(message, server.id, channel.id, emoji_to_action)

    # print("STOPPPP... old,")
    # print(current_help)
    

    # print("STOPPPP... new,")
    # print(current_help)
    

def get_help_content(bot, existing_text, user_id, node, node_name):
    topics = Help.get_topics_for(node)

    emoji_to_action = []
    message_body = ""
    for topic in topics:
        emoji = Utilities.get_emoji(bot, topic[0])
        message_body += f"{emoji} {topic[1]}\n"

        emoji_action = f"help.{topic[3]}.{user_id}"
        emoji_to_action.append((emoji, emoji_action))

    message_string = f"{node_name}\n{message_body}"
    new_message_string = f"{existing_text}{message_string}"
    return (new_message_string, emoji_to_action)

async def add_reactions(message, server_id, channel_id, emoji_to_action):
    global current_help 
    instance_uuid = str(uuid.uuid4())
    current_help = instance_uuid

    for emoji, action in emoji_to_action:
        print("adding... currently,")
        print(current_help)
        if current_help == instance_uuid:
            ReactionActions.save_reaction_action(server_id, channel_id, message.id, emoji.id, action)
            await message.add_reaction(emoji)
        else:
            print("New...")
            await message.clear_reactions()
            await perform_queued_continue()

            break

    
    current_help = ""


async def perform_queued_continue():
    global current_help 
    global queued_message
    global queued_server_id
    global queued_channel_id
    global queued_emoji_to_action

    await add_reactions(
        queued_message,
        queued_server_id,
        queued_channel_id,
        queued_emoji_to_action
    )

    current_help = None
    queued_message = None
    queued_server_id = None
    queued_channel_id = None
    queued_emoji_to_action = None

    # if 



    # instance_uuid = str(uuid.uuid4())
    # current_help = instance_uuid

    # topic_tree = Help.parse_tree()
    # topics = Help.get_topics_for(topic_tree) # array of tuples
    # print(topics)

    # emoji_and_action = []
    # message_body = ""
    # for topic in topics:
    #     emoji = Utilities.get_emoji(bot, topic[0])
    #     message_body += f"{emoji} {topic[1]}\n"

    #     emoji_action = f"help.{topic[3]}.{ctx.author.id}"
    #     emoji_and_action.append((emoji, emoji_action))

    # message_string = f"{topic_tree.name}\n{message_body}"
    # message = await ctx.send(message_string)

    # server = ctx.guild
    # channel = message.channel

    # for emoji, action in emoji_and_action:
    #     if current_help == instance_uuid:
    #         ReactionActions.save_reaction_action(server.id, channel.id, message.id, emoji.id, action)
    #         await message.add_reaction(emoji)
    #     else:
    #         print("New...")


# async def continaue_help(bot, message, id, session_user_id):
#     print("h")
#     print(message.content)

#     existing_content = message.content
#     existing_message_string = existing_content + "\n\n⇣\n\n"

#     topic_tree = Help.parse_tree()
    
#     node = search.find(topic_tree, lambda node: f"{id}<->" in node.name)
#     node_name = Help.get_name_for(node)[2]

#     print(RenderTree(node))
#     topics = Help.get_topics_for(node) # array of tuples

#     emoji_and_action = []
#     message_body = ""
#     for topic in topics:
#         emoji = Utilities.get_emoji(bot, topic[0])

#         print("Emo... ")
#         print(emoji)

#         message_body += f"{emoji} {topic[1]}\n"

#         emoji_action = f"help.{topic[3]}.{session_user_id}"
#         emoji_and_action.append((emoji, emoji_action))

#     message_string = f"{node_name}\n{message_body}"
#     new_message_string = f"{existing_message_string}{message_string}"
#     edited_message = await message.edit(content=new_message_string)


# returns a message + map of emoji to action