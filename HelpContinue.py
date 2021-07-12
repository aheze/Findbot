# import Help
# import Utilities
# from anytree import Node, RenderTree, search

# async def continue_help(bot, message, id, session_user_id):
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

#     # server = ctx.guild
#     # channel = message.channel

#     # for emoji, action in emoji_and_action:
#     #     save_reaction_action(server.id, channel.id, message.id, emoji.id, action)
#     #     await message.add_reaction(emoji)


#     # print("node... ")
#     # print(node)
