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

class HelpButtonView(discord.ui.View):
    session_message = None

    def __init__(self, bot, session_user_id, previous_digit_id, current_digit_id, emoji_to_digit):
        super().__init__(timeout=180)
        self.bot = bot
        self.session_user_id = session_user_id

        print("PREVIOUS digit id???")
        print(previous_digit_id)

        if previous_digit_id != 0:
            print(f"UNDO BUTTON TO ID: {previous_digit_id}")
            emoji = bot.get_emoji(873335307372724304)
            self.add_item(HelpButton(bot, session_user_id, emoji, current_digit_id, previous_digit_id))
            print("added!")
        for emoji, to_digit_id in emoji_to_digit:
            if emoji.name != "Currently_Unavailable":
                self.add_item(HelpButton(bot, session_user_id, emoji, current_digit_id, to_digit_id))

    async def on_timeout(self) -> None:
        matching_helps = [x for x in helps if x.session_message if x.session_message.id == self.session_message.id]
        continued_help = matching_helps[0]
        await continued_help.set_timeout()
        return await super().on_timeout()


class HelpContent:
    def __init__(self, message_string=None, message_buttons_view=None, embed_file=None, embed=None):
        print("Making init!")
        self.message_string = message_string
        self.message_buttons_view = message_buttons_view
        self.embed_file = embed_file 
        self.embed = embed 

class HelpButton(discord.ui.Button):
    def __init__(self, bot, session_user_id, emoji, current_digit_id, to_digit_id):
        label = ""
        if "_" not in emoji.name:
            label = emoji.name

        super().__init__(label=label, emoji=emoji, style=discord.ButtonStyle.blurple)
        self.bot = bot
        self.emoji = emoji
        self.session_user_id = session_user_id
        self.current_digit_id = current_digit_id
        self.to_digit_id = to_digit_id

    async def callback(self, interaction: discord.Interaction):   
        print("-=-=-=-=-=-==--=-=-==-button pressed!")   
        print(f"Going towards {self.to_digit_id}, current button id be {self.current_digit_id}")     
        await continue_help(self.bot, interaction.channel, interaction.message, self.session_user_id, self.current_digit_id, self.to_digit_id) 
        # await continue_help(self.bot, interaction.guild, interaction.channel, interaction.message, self.to_digit_id, self.session_user_id, self.emoji.id, self.current_digit_id)
        
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

async def continue_help(bot, channel, message, session_user_id, previous_digit_id, to_digit_id):
    matching_helps = [x for x in helps if x.session_message if x.session_message.id == message.id]
    continued_help = matching_helps[0]
    await continued_help.continue_help(bot, channel, session_user_id, previous_digit_id, to_digit_id)
    # await continued_help.continue_help(bot, server, channel, message, id, session_user_id, emoji_id, current_digit_id)

class HelpFactory:
    session_message = None

    async def set_timeout(self, timed_out = True):
        if self.session_message:
            if timed_out:
                channel = self.session_message.channel
                updated_message = await channel.fetch_message(self.session_message.id)
                existing_message_string = updated_message.content + "\n〰〰〰〰〰\n"
                new_message = existing_message_string + "*Session timed out - type `.help` to start a new one!*"
                await self.session_message.edit(content=new_message, view=None)

    async def generate_help_message(self, bot, channel, session_user_id, previous_digit_id, to_digit_id=None, jump_node=None):
        print("generating..")
        print(f"generating to: {to_digit_id}")

        topic_tree = HelpBase.parse_tree()
        if to_digit_id:
            node = search.findall(topic_tree, lambda node: f"{to_digit_id}<->" in node.name)[0]
        elif jump_node:
            node = jump_node
        else:
            node = topic_tree

        string = ""
        view = None
        file = None
        embed = None

        text = None
        emoji_to_digit = None
        done = None
        instructions = None

        for index, child in enumerate(node.path):
            if index == 0:
                greeting_name = child.name.replace("<Hello>", self.greeting)
                text, emoji_to_digit, _, _ = self.get_help_content(bot, "", child, greeting_name, True)
                string = string + text
            else:
                node_info = HelpBase.get_node_info(child, emoji_selected=False)
                emoji = Utilities.get_specific_emoji(bot, [871866926173921320, 871866989294006382], node_info.emoji_name)
                replaced_existing = HelpBase.replace_previous_with_unselected_emoji(bot, string, emoji.id)
                existing_message_string = replaced_existing + "〰〰〰〰〰\n"
                text, emoji_to_digit, done, instructions = self.get_help_content(bot, "", child, node_info.selected_header_name, False)

                text = HelpBase.sub_server_stats(text, channel.guild)
                string = existing_message_string + text

        # is last node in the tree, so add reactions and handle actions
        if index == len(node.path) - 1:
            print("prev dig id:")
            print(previous_digit_id)
            # view = HelpButtonView(bot, session_user_id, emoji_to_digit, current_digit_id)

            view = HelpButtonView(
                bot=bot,
                session_user_id=session_user_id,
                previous_digit_id=previous_digit_id,
                current_digit_id=to_digit_id,
                emoji_to_digit=emoji_to_digit
            )

            if instructions:
                if instructions == "attachment":
                    url = HelpActions.determine_action(node_info.selected_header_name)
                    file = discord.File(url, filename="image.png")
                    embed = discord.Embed()
                    embed_url = 'attachment://image.png'
                    embed.set_image(url=embed_url)

        content = HelpContent(
            message_string=string,
            message_buttons_view=view,
            embed_file=file,
            embed=embed
        )

        return content
    async def jump(self, bot, ctx, letter_id):
        self.greeting = Utilities.random_message("greeting", ctx.author.mention)
        node = HelpBase.jump_to_node(letter_id)

        content = await self.generate_help_message(
            bot=bot,
            channel=ctx.channel,
            session_user_id=ctx.author.id,
            previous_digit_id=0,
            current_digit_id=0,
            jump_node=node
        )

        
        message = await ctx.send(content.message_string, view=content.message_buttons_view)
        self.session_message = message
        content.message_buttons_view.session_message = message

        if content.embed_file and content.embed:
            await ctx.send(file=content.embed_file, embed=content.embed)

    async def start_help(self, bot, ctx):
        print("starting")
        self.greeting = Utilities.random_message("greeting", ctx.author.mention)
        print("abotu to get")


        # async def generate_help_message(self, bot, channel, session_user_id, previous_digit_id, to_digit_id=None, jump_node=None):
        content = await self.generate_help_message(
            bot=bot,
            channel=ctx.channel,
            session_user_id=ctx.author.id,
            previous_digit_id=None,
            to_digit_id=0
        )

        message = await ctx.channel.send(content.message_string, view=content.message_buttons_view)
        self.session_message = message
        content.message_buttons_view.session_message = message

    async def continue_help(self, bot, channel, session_user_id, previous_digit_id, to_digit_id):
        print(f"continuing... preious was {previous_digit_id}, now {to_digit_id}")
        content = await self.generate_help_message(
            bot=bot,
            channel=channel,
            session_user_id=session_user_id,
            previous_digit_id = previous_digit_id,
            to_digit_id=to_digit_id
        )

        # generate_help_message(self, bot, channel, session_user_id, current_digit_id=None, to_digit_id=None, jump_node=None):
        await self.session_message.edit(content.message_string, view=content.message_buttons_view)
        if content.embed_file and content.embed:
            await channel.send(file=content.embed_file, embed=content.embed)


    def get_help_content(self, bot, existing_text, node, node_name, selected_emoji_version):
        done = False
        additional_instructions = None

        child_node_infos = HelpBase.get_child_node_infos(node, selected_emoji_version)
        emoji_to_digit = []
        message_body = ""

        if len(child_node_infos) > 0:
            for node_info in child_node_infos:
                emoji = Utilities.get_specific_emoji(bot, [871866926173921320, 871866989294006382], node_info.emoji_name)
                
                message_body += f"{emoji} {node_info.options_name}\n"
                emoji_to_digit.append((emoji, node_info.digit_id))

            message_string = f"{node_name}\n{message_body}"
        else:
            done = True
            message_string = node_name + "\n"

            if node_name.startswith("<a>"):
                message_string = ""
                additional_instructions = "attachment"

        
        new_message_string = f"{existing_text}{message_string}"
        return (new_message_string, emoji_to_digit, done, additional_instructions)


        
