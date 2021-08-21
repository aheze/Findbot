from discord import guild
import HelpBase
import Utilities
import HelpActions
from datetime import datetime, timedelta
from anytree import search
import discord

helps = []

class HelpButtonView(discord.ui.View):
    session_message = None

    def __init__(self, bot, session_user_id, previous_digit_id, current_digit_id, emoji_to_digit):
        super().__init__(timeout=180)
        self.bot = bot
        self.session_user_id = session_user_id
        self.current_digit_id = current_digit_id

        if previous_digit_id != 0:
            emoji = bot.get_emoji(873335307372724304)
            self.add_item(HelpButton(bot, session_user_id, emoji, previous_digit_id, discord.ButtonStyle.gray))
        for emoji, to_digit_id in emoji_to_digit:
            if emoji.name != "Currently_Unavailable":
                self.add_item(HelpButton(bot, session_user_id, emoji, to_digit_id, discord.ButtonStyle.blurple))

        if len(emoji_to_digit) == 0:
            self.add_item(HelpFinishButton(bot, current_digit_id))
            

    async def on_timeout(self) -> None:
        matching_helps = [x for x in helps if x.session_message if x.session_message.id == self.session_message.id]
        if len(matching_helps) > 0:
            continued_help: HelpFactory = matching_helps[0]
            await continued_help.send_archived_help(
                view=self,
                bot=self.bot,
                guild=self.session_message.guild,
                digit_id=self.current_digit_id,
                timed_out=True
            )

        return await super().on_timeout()


class HelpContent:
    def __init__(self, message_string=None, message_buttons_view=None, embed_file=None, embed=None):
        self.message_string = message_string
        self.message_buttons_view = message_buttons_view
        self.embed_file = embed_file 
        self.embed = embed 

class HelpFinishButton(discord.ui.Button):
    def __init__(self, bot, current_digit_id):
        emoji = bot.get_emoji(873703213898014730)
        super().__init__(label="Done", emoji=emoji, style=discord.ButtonStyle.green)
        self.bot = bot
        self.current_digit_id = current_digit_id

    async def callback(self, interaction: discord.Interaction): 
        matching_helps = [x for x in helps if x.session_message if x.session_message.id == interaction.message.id]
        if len(matching_helps) > 0:
            continued_help: HelpFactory = matching_helps[0]
            await continued_help.send_archived_help(
                view=None,
                bot=self.bot,
                guild=interaction.message.guild,
                digit_id=self.current_digit_id,
                timed_out=False
            )

class HelpButton(discord.ui.Button):
    def __init__(self, bot, session_user_id, emoji, to_digit_id, style):
        label = ""
        if "_" not in emoji.name:
            label = emoji.name

        super().__init__(label=label, emoji=emoji, style=style)
        clean_emoji = Utilities.get_specific_emoji(bot, [873661221436551178], emoji.name)
        self.bot = bot
        self.emoji = clean_emoji
        self.session_user_id = session_user_id
        self.to_digit_id = to_digit_id

    async def callback(self, interaction: discord.Interaction): 
        await continue_help(self.bot, interaction.channel, interaction.message, self.session_user_id, self.to_digit_id) 

async def help(bot, ctx, args):
    global helps
    help = HelpFactory()
    helps.append(help)

    combined = "".join(args).strip()

    if combined:
        await help.jump(bot, ctx, combined)
    else:
        await help.start_help(bot, ctx)

async def continue_help(bot, channel, message, session_user_id, to_digit_id):
    matching_helps = [x for x in helps if x.session_message if x.session_message.id == message.id]
    if len(matching_helps) > 0:
        continued_help = matching_helps[0]
        await continued_help.continue_help(bot, channel, session_user_id, to_digit_id)

class HelpFactory:
    session_message = None
    session_user = None
    active_view = None
    done = False

    async def generate_help_message(self, bot, channel, session_user_id, to_digit_id=None, jump_node=None):
        topic_tree = HelpBase.parse_tree(channel.guild.id)
        if to_digit_id:
            if to_digit_id == -1:
                node = topic_tree
            else:
                nodes = search.findall(topic_tree, lambda node: f"{to_digit_id}<->" in node.name)
                if len(nodes) > 0:
                    node = nodes[0]
                else:
                    node = topic_tree
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
                self.done = done

                text = HelpBase.sub_server_stats(text, channel.guild)
                string = existing_message_string + text

                if instructions and node_info:
                    if instructions == "attachment":
                        url = HelpActions.determine_action(channel.guild.id, node_info.selected_header_name)
                        file = discord.File(url, filename="image.png")
                        embed = discord.Embed()
                        embed_url = 'attachment://image.png'
                        embed.set_image(url=embed_url)

        # is last node in the tree, so add reactions and handle actions
        if index == len(node.path) - 1:
            if node.parent:
                node_info = HelpBase.get_node_info(node.parent, emoji_selected=False)
                if node_info:
                    previous_node_id = node_info.digit_id

                    view = HelpButtonView(
                        bot=bot,
                        session_user_id=session_user_id,
                        previous_digit_id=previous_node_id,
                        current_digit_id=to_digit_id,
                        emoji_to_digit=emoji_to_digit
                    )
                else:
                    view = HelpButtonView(
                        bot=bot,
                        session_user_id=session_user_id,
                        previous_digit_id=-1,
                        current_digit_id=to_digit_id,
                        emoji_to_digit=emoji_to_digit
                    )
            else:
                view = HelpButtonView(
                    bot=bot,
                    session_user_id=session_user_id,
                    previous_digit_id=0,
                    current_digit_id=to_digit_id,
                    emoji_to_digit=emoji_to_digit
                )


        content = HelpContent(
            message_string=string,
            message_buttons_view=view,
            embed_file=file,
            embed=embed
        )
        return content

    async def send_archived_help(self, view, bot, guild, digit_id, timed_out):
        global helps

        if view:
            if self.active_view != view:
                return

        path_string = ""
        content_string = ">>> "
        letter_id = ""

        topic_tree = HelpBase.parse_tree(guild.id)
        nodes = search.findall(topic_tree, lambda node: f"{digit_id}<->" in node.name)
        if len(nodes) > 0:
            node = nodes[0]
            letter_id = HelpBase.generate_identifier_for_node(node)
        else:
            node = topic_tree


        for index, child in enumerate(node.path):
            if index == 0:
                path_string = f"Help session for {self.session_user.mention}"
            else:
                node_info = HelpBase.get_node_info(child, emoji_selected=False)
                text = HelpBase.sub_server_stats(node_info.options_name, guild)
                path_string = path_string + " → " + f"**{text}**"

            if index == len(node.path) - 1:
                if index == 0:
                    path_string += ":"
                    child_node_infos = HelpBase.get_child_node_infos(node, child)
                    text = ""
                    for node_info in child_node_infos:
                        emoji = Utilities.get_specific_emoji(bot, [871866926173921320, 871866989294006382], node_info.emoji_name)

                        text += f"{emoji} {node_info.options_name}\n"
                    content_string += text
                else:
                    node_info = HelpBase.get_node_info(child, emoji_selected=False)
                    text, _, _, _ = self.get_help_content(bot, "", child, node_info.selected_header_name, False)
                    text = HelpBase.sub_server_stats(text, guild)
                    content_string += text
    
        timed_out_part = ""
        if timed_out:
            if letter_id:
                timed_out_part = f"〰〰〰〰〰\n*Session timed out - type `.help {letter_id}` to continue*"
            else:
                timed_out_part = f"〰〰〰〰〰\n*Session timed out - type `.help` to start a new session*"
            combined_string = f"{path_string}\n{content_string}{timed_out_part}"
        else:
            combined_string = f"{path_string}\n{content_string}"

        # remove from the `helps` list
        helps = [help for help in helps if help.session_message if help.session_message.id != self.session_message.id]

        await self.session_message.edit(combined_string, view=None)

    async def jump(self, bot, ctx, letter_id):
        self.greeting = Utilities.random_message("greeting", ctx.guild.id, ctx.author.mention)
        if self.greeting is None:
            self.greeting = "Help?"

        self.session_user = ctx.author
        node = HelpBase.jump_to_node(ctx.guild.id, letter_id)


        node_info = HelpBase.get_node_info(node)
        print(node_info.digit_id)

        if node_info:
            content = await self.generate_help_message(
                bot=bot,
                channel=ctx.channel,
                session_user_id=ctx.author.id,
                to_digit_id = node_info.digit_id
            )
        else:
            content = await self.generate_help_message(
                bot=bot,
                channel=ctx.channel,
                session_user_id=ctx.author.id,
                jump_node=node
            )

        message = await ctx.send(content.message_string, view=content.message_buttons_view)
        self.session_message = message
        content.message_buttons_view.session_message = message
        self.active_view = content.message_buttons_view

        if content.embed_file and content.embed:
            await self.session_message.reply(file=content.embed_file, embed=content.embed)

    async def start_help(self, bot, ctx):
        self.greeting = Utilities.random_message("greeting", ctx.guild.id, ctx.author.mention)
        if self.greeting is None:
            self.greeting = "Help?"

        self.session_user = ctx.author

        content = await self.generate_help_message(
            bot=bot,
            channel=ctx.channel,
            session_user_id=ctx.author.id
        )

        message = await ctx.channel.send(content.message_string, view=content.message_buttons_view)
        self.session_message = message
        content.message_buttons_view.session_message = message
        self.active_view = content.message_buttons_view

    async def continue_help(self, bot, channel, session_user_id, to_digit_id):

        content = await self.generate_help_message(
            bot=bot,
            channel=channel,
            session_user_id=session_user_id,
            to_digit_id = to_digit_id
        )
        await self.session_message.edit(content.message_string, view=content.message_buttons_view)
        content.message_buttons_view.session_message = self.session_message
        self.active_view = content.message_buttons_view

        if content.embed_file and content.embed:
            await self.session_message.reply(file=content.embed_file, embed=content.embed)


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

            if "<a>" in node_name:
                action_split = node_name.split("<a>")
                message_string = action_split[0] + "\n"
                additional_instructions = "attachment"

        
        new_message_string = f"{existing_text}{message_string}"
        return (new_message_string, emoji_to_digit, done, additional_instructions)


        
