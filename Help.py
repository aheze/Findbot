import HelpBase
import Utilities
import ReactionActions
import HelpActions
import FileContents
import TimedActions
import uuid
from datetime import datetime, timedelta
import asyncio
from anytree import Node, RenderTree, search
import discord

helps = []

async def help(bot, ctx, args):
    global helps
    help = HelpFactory()
    helps.append(help)

    combined = "".join(args).strip()

    if combined:
        await help.jump(bot, ctx, combined)
    else:
        await help.start_help(bot, ctx)

async def continue_help(bot, server, channel, message, id, session_user_id, emoji_id):
    matching_helps = [x for x in helps if x.session_message if x.session_message.id == message.id]
    continued_help = matching_helps[0]
    await continued_help.continue_help(bot, server, channel, message, id, session_user_id, emoji_id)

async def remove_lingering_helps():
    global helps

    for help in helps:
        await help.set_timeout()

    helps.clear()

    with open('Config/HelpLog.txt', 'w') as file:
        file.write("")

async def clean_up_helps():
    global helps

    while True:
        new_file_contents = []
        with open('Output/HelpLog.txt', 'r') as file:
            file_contents = FileContents.get_file_contents(file)
            
            for line in file_contents:
                components = line.strip().split(":") # 0 is time, 1 is message id
                time = TimedActions.convert_string_to_date(components[0])

                if datetime.now() - timedelta(minutes=5) > time: # execute action, delete line
                    matching_helps = [(index, x) for (index, x) in enumerate(helps) if x.session_message if x.session_message.id == int(components[1])]

                    if len(matching_helps) > 0:
                        expired_help = matching_helps[0]

                        expired_help_index = expired_help[0]
                        expired_help_object = expired_help[1]
                        await expired_help_object.set_timeout()
                        del helps[expired_help_index]
                    else:
                        new_file_contents.append(line)
                else:
                    new_file_contents.append(line)
        with open('Output/HelpLog.txt', 'w') as file:
            combined = FileContents.combine_file_contents(new_file_contents)
            file.write(combined)

        await asyncio.sleep(20)


class HelpFactory:
    session_start_date_string = None
    session_message = None

    current_help = None
    queued_message = None
    queued_server_id = None
    queued_channel_id = None
    queued_emoji_to_action = None

    done = False
    timed_out = False

    def save_help(self, start_date_string, message_id):
        with open('Output/HelpLog.txt', 'a') as file:
            string = f"{start_date_string}:{message_id}\n"
            file.write(string)

    async def set_timeout(self, timed_out = True):
        if not self.done:
            self.done = True

            if self.session_message:
                server = self.session_message.guild
                channel = self.session_message.channel
                
                if self.current_help:
                    self.current_help = str(uuid.uuid4())
                    self.queued_server_id = server.id
                    self.queued_channel_id = channel.id
                    self.timed_out = timed_out
                else:
                    ReactionActions.cleanup_message_reactions(server.id, channel.id, self.session_message.id)
                    if self.session_message:
                        await self.session_message.clear_reactions()
                    if timed_out:
                        updated_message = await channel.fetch_message(self.session_message.id)
                        existing_message_string = updated_message.content + "\n〰〰〰〰〰\n"
                        new_message = existing_message_string + "*Session timed out - type `.help` to start a new one!*"
                        await self.session_message.edit(content=new_message)

    async def perform_queued_continue(self):
        if self.done:
            ReactionActions.cleanup_message_reactions(self.queued_server_id, self.queued_channel_id, self.session_message.id)
            await self.session_message.clear_reactions()
            if self.timed_out:
                channel = self.session_message.channel
                updated_message = await channel.fetch_message(self.session_message.id)
                existing_message_string = updated_message.content + "\n〰〰〰〰〰\n"
                new_message = existing_message_string + "*Session timed out - type `.help` to start a new one!*"
                await self.session_message.edit(content=new_message)
        else:
            await self.add_reactions(
                self.queued_message,
                self.queued_server_id,
                self.queued_channel_id,
                self.queued_emoji_to_action
            )

    async def jump(self, bot, ctx, letter_id):
        node = HelpBase.jump_to_node(letter_id)
        greeting = Utilities.random_message("greeting", ctx.author.mention)

        server = ctx.guild
        channel = ctx.channel

        string = ""
        for index, child in enumerate(node.path):
            print("Loop.")
            if index == 0:
                greeting = Utilities.random_message("greeting", ctx.author.mention)
                greeting_name = greeting.replace("<Hello>", greeting)
                text, emoji_to_action, _, _ = self.get_help_content(bot, "", ctx.author.id, child, greeting_name, True)
                string += text
            else:
                node_info = HelpBase.get_node_info(child, emoji_selected=False)
                print(f"nodeinfo: {node_info}")
                print(f"em name: {node_info.emoji_name}")
                emoji = Utilities.get_specific_emoji(bot, [871866926173921320, 871866989294006382], node_info.emoji_name)
                print(f"emoji: {emoji}")
                replaced_existing = HelpBase.replace_previous_with_unselected_emoji(bot, string, emoji.id)
                existing_message_string = replaced_existing + "〰〰〰〰〰\n"
                text, emoji_to_action, done, instructions = self.get_help_content(bot, "", ctx.author.id, child, node_info.selected_header_name, False)
                text = HelpBase.sub_server_stats(text, server)
                string = existing_message_string + text

            print(f"string: {string}")

            # is last node in the tree, so add reactions and handle actions
            if index == len(node.path) - 1:
                if done:
                    await self.set_timeout(False)

                message = await ctx.send(string)

                if instructions == "attachment":
                    if server and channel:
                        url = HelpActions.determine_action(node_info.selected_header_name)
                        print(f"URL: {url}")
                        file = discord.File(url, filename="image.png")
                        embed = discord.Embed()
                        embed_url = 'attachment://image.png'
                        embed.set_image(url=embed_url)
                        await channel.send(file=file, embed=embed)

                server = ctx.guild
                channel = message.channel

                now = datetime.now()
                self.session_start_date_string = TimedActions.convert_date_to_string(now)
                self.session_message = message
                self.save_help(self.session_start_date_string, self.session_message.id)
                await self.add_reactions(message, server.id, channel.id, emoji_to_action)

    async def start_help(self, bot, ctx):
        topic_tree = HelpBase.parse_tree()
        name = topic_tree.name
        greeting = Utilities.random_message("greeting", ctx.author.mention)
        name = name.replace("<Hello>", greeting)

        text, emoji_to_action, _, _ = self.get_help_content(bot, "", ctx.author.id, topic_tree, name, True)
        message = await ctx.send(text)

        server = ctx.guild
        channel = message.channel

        now = datetime.now()
        self.session_start_date_string = TimedActions.convert_date_to_string(now)
        self.session_message = message
        self.save_help(self.session_start_date_string, self.session_message.id)

        await self.add_reactions(message, server.id, channel.id, emoji_to_action)

    async def continue_help(self, bot, server, channel, message, topic_id, session_user_id, emoji_id):
        existing_content = message.content
        replaced_existing = HelpBase.replace_previous_with_unselected_emoji(bot, existing_content, emoji_id)
        existing_message_string = replaced_existing + "\n〰〰〰〰〰\n"
        topic_tree = HelpBase.parse_tree()
        node = search.findall(topic_tree, lambda node: f"{topic_id}<->" in node.name)[0]

        node_info = HelpBase.get_node_info(node)
        letter_id = HelpBase.generate_identifier_for_node(node)

        text, emoji_to_action, done, instructions = self.get_help_content(bot, existing_message_string, session_user_id, node, node_info.selected_header_name, False)
        if done:
            await self.set_timeout(False)

        text = HelpBase.sub_server_stats(text, server)

        member = server.get_member(session_user_id)
        member_roles = [role for role in member.roles if role.name == "Android" or role.name == "Finder"]
        if len(member_roles) > 0:
            note_embed = discord.Embed(description=f"Get here again by typing `.help {letter_id}`", color=0x34ebeb)
            await message.edit(embed=note_embed, content=text)
        else:
            await message.edit(content=text)

        if instructions == "attachment":
            url = HelpActions.determine_action(node_info.selected_header_name)
            file = discord.File(url, filename="image.png")
            embed = discord.Embed()
            embed_url = 'attachment://image.png'
            embed.set_image(url=embed_url)
            await channel.send(file=file, embed=embed)

        if self.current_help:
            self.current_help = str(uuid.uuid4())
            self.queued_message = message
            self.queued_server_id = server.id
            self.queued_channel_id = channel.id
            self.queued_emoji_to_action = emoji_to_action
        else:
            await message.clear_reactions()
            await self.add_reactions(message, server.id, channel.id, emoji_to_action)

    def get_help_content(self, bot, existing_text, user_id, node, node_name, selected_emoji_version):
        done = False
        additional_instructions = None

        child_node_infos = HelpBase.get_child_node_infos(node, selected_emoji_version)
        emoji_to_action = []
        message_body = ""
        
        if len(child_node_infos) > 0:
            for node_info in child_node_infos:
                emoji = Utilities.get_specific_emoji(bot, [871866926173921320, 871866989294006382], node_info.emoji_name)
                
                message_body += f"{emoji} {node_info.options_name}\n"
                
                emoji_action = f"help.{node_info.digit_id}.{user_id}"
                emoji_to_action.append((emoji, emoji_action))

            message_string = f"{node_name}\n{message_body}"
        else:
            done = True
            message_string = node_name + "\n"

            if node_name.startswith("<a>"):
                message_string = ""
                additional_instructions = "attachment"

        
        new_message_string = f"{existing_text}{message_string}"

        return (new_message_string, emoji_to_action, done, additional_instructions)

    async def add_reactions(self, message, server_id, channel_id, emoji_to_action):
        instance_uuid = str(uuid.uuid4())
        self.current_help = instance_uuid

        has_conflict = False
        for emoji, action in emoji_to_action:
            if self.current_help == instance_uuid:
                ReactionActions.save_reaction_action(server_id, channel_id, message.id, emoji.id, action)
                if emoji.name != "Currently_Unavailable":
                    await message.add_reaction(emoji)
            else:
                has_conflict = True
                break
        
        if self.current_help != instance_uuid:
            has_conflict = True

        if has_conflict:
            await message.clear_reactions()
            await self.perform_queued_continue()
        else:
            self.current_help = None
            self.queued_message = None
            self.queued_server_id = None
            self.queued_channel_id = None
            self.queued_emoji_to_action = None

    

        
