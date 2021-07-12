import HelpBase
import Utilities
import ReactionActions
import uuid
from anytree import Node, RenderTree, search

helps = []

async def help(bot, ctx):
    global helps
    help = HelpFactory()
    helps.append(help)
    await help.start_help(bot, ctx)

async def continue_help(bot, server, channel, message, id, session_user_id):
    matching_helps = [x for x in helps if x.session_message_id == message.id]
    print(matching_helps)
    continued_help = matching_helps[0]
    await continued_help.continue_help(bot, server, channel, message, id, session_user_id)

class HelpFactory:
    session_message_id = None
    current_help = None
    queued_message = None
    queued_server_id = None
    queued_channel_id = None
    queued_emoji_to_action = None

    async def start_help(self, bot, ctx):
        global session_message_id
        topic_tree = HelpBase.parse_tree()

        text, emoji_to_action = self.get_help_content(bot, "", ctx.author.id, topic_tree, topic_tree.name)
        message = await ctx.send(text)
        self.session_message_id = message.id

        server = ctx.guild
        channel = message.channel
        await self.add_reactions(message, server.id, channel.id, emoji_to_action)

    async def continue_help(self, bot, server, channel, message, id, session_user_id):
        existing_content = message.content
        existing_message_string = existing_content + "\n\n⇣\n\n"
        topic_tree = HelpBase.parse_tree()
        node = search.find(topic_tree, lambda node: f"{id}<->" in node.name)
        node_name = HelpBase.get_name_for(node)[2]

        text, emoji_to_action = self.get_help_content(bot, existing_message_string, session_user_id, node, node_name)
        edited_message = await message.edit(content=text)

        if self.current_help:
            self.current_help = str(uuid.uuid4())
            self.queued_message = message
            self.queued_server_id = server.id
            self.queued_channel_id = channel.id
            self.queued_emoji_to_action = emoji_to_action
        else:
            await message.clear_reactions()
            await self.add_reactions(message, server.id, channel.id, emoji_to_action)

    def get_help_content(self, bot, existing_text, user_id, node, node_name):
        topics = HelpBase.get_topics_for(node)

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

    async def add_reactions(self, message, server_id, channel_id, emoji_to_action):

        instance_uuid = str(uuid.uuid4())
        self.current_help = instance_uuid

        for emoji, action in emoji_to_action:
            if self.current_help == instance_uuid:
                ReactionActions.save_reaction_action(server_id, channel_id, message.id, emoji.id, action)
                await message.add_reaction(emoji)
            else:
                print("STOPPPp")
                await message.clear_reactions()
                await self.perform_queued_continue()
                break
        
        self.current_help = None


    async def perform_queued_continue(self):

        await self.add_reactions(
            self.queued_message,
            self.queued_server_id,
            self.queued_channel_id,
            self.queued_emoji_to_action
        )

        self.current_help = None
        self.queued_message = None
        self.queued_server_id = None
        self.queued_channel_id = None
        self.queued_emoji_to_action = None
