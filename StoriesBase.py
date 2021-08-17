import FileContents
import Stories
import discord
from anytree import Node, RenderTree, search
from datetime import datetime, timedelta

TIME_FORMATTING = "%m/%d/%y"

class StoryChooserButton(discord.ui.Button):
    def __init__(self, bot, guide, channel, reader_user, story):
        super().__init__(label="Start", style=discord.ButtonStyle.green)
        
        self.bot = bot
        self.guide = guide
        self.channel = channel
        self.reader_user = reader_user
        self.story = story

        if story:
            self.disabled = False
        else:
            self.disabled = True

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(view=None)
        await Stories.start_story(
            bot=self.bot,
            guide=self.guide,
            channel=self.channel,
            reader_user=self.reader_user,
            embed_message=interaction.message,
            story=self.story
        )

class StoryChooserDropdown(discord.ui.Select):
    def __init__(self, bot, guide, channel, reader_user, stories, selected_story_index=None):

        self.bot = bot
        self.guide = guide
        self.channel = channel
        self.reader_user = reader_user
        self.stories = stories

        options = []
        for index, story in enumerate(stories):
            description = f"By {story.author}"
            if story.date:
                date_string = story.date.strftime(TIME_FORMATTING)
                description = f"By {story.author} • {date_string}"


            if selected_story_index is not None:
                if selected_story_index == index:
                    option = discord.SelectOption(label=story.title, description=description, default=True, emoji=story.emoji)
                else:   
                    option = discord.SelectOption(label=story.title, description=description, emoji=story.emoji)
            else:
                option = discord.SelectOption(label=story.title, description=description, emoji=story.emoji)
            options.append(option)
        
        super().__init__(placeholder='Choose a story', options=options)


    async def callback(self, interaction: discord.Interaction):

        for index, story in enumerate(self.stories):
            if story.title == self.values[0]:
                break
        else:
            index = -1

        view = StoryDropdownChooserView(
            bot=self.bot,
            guide=self.guide,
            channel=self.channel,
            reader_user=self.reader_user,
            stories=self.stories,
            selected_story_index=index
        )
        story = self.stories[index]
        embed = discord.Embed(title=story.title, description=f"{story.description}", color=0x00aeef)
        embed.set_image(url=story.image)

        reader = self.channel.guild.get_member_named(story.author)
        description = f"By {story.author}"
        if story.date:
            date_string = story.date.strftime(TIME_FORMATTING)
            description = f"By {story.author} • {date_string}"
        if reader:
            embed.set_footer(text=description, icon_url=reader.avatar.url)
        else:
            embed.set_footer(text=description)

        await interaction.response.edit_message(embed=embed, view=view)

class StoryDropdownChooserView(discord.ui.View):
    selected_story = None
    def __init__(self, bot, guide, channel, reader_user, stories, selected_story_index=None):
        self.reader_user = reader_user
        super().__init__()

        self.add_item(StoryChooserDropdown(bot, guide, channel, reader_user, stories, selected_story_index))
        if selected_story_index is not None:
            if len(stories) > selected_story_index:
                self.add_item(StoryChooserButton(bot, guide, channel, reader_user, stories[selected_story_index]))
            else:
                self.add_item(StoryChooserButton(bot, guide, channel, reader_user, None))
        else:
            self.add_item(StoryChooserButton(bot, guide, channel, reader_user, None))


    async def interaction_check(self, interaction):
        return interaction.user == self.reader_user or interaction.user.id == 743230678795288637

class StoryButtonView(discord.ui.View):
    session_message = None

    def __init__(self, bot, guide, thread, reader_user, story, next_button_infos):
        super().__init__(timeout=None)
        self.bot = bot
        self.guide = guide
        self.thread = thread
        self.reader_user = reader_user

        for next_button_info in next_button_infos:

            self.add_item(
                StoryButton(
                    bot=bot,
                    guide=guide,
                    thread=thread,
                    reader_user=reader_user,
                    story=story,
                    label=next_button_info.name,
                    to_id=next_button_info.id
                )
            )

    async def interaction_check(self, interaction):
        return interaction.user == self.reader_user or interaction.user.id == 743230678795288637

class StoryButton(discord.ui.Button):
    def __init__(self, bot, guide, thread, reader_user, story, label, to_id):
        super().__init__(label=label, style=discord.ButtonStyle.gray)
        self.bot = bot
        self.guide = guide
        self.thread = thread
        self.reader_user = reader_user
        self.story = story
        self.label = label
        self.to_id = to_id

    async def callback(self, interaction: discord.Interaction):
        self.style = discord.ButtonStyle.blurple
        for button in self.view.children:
            button.disabled = True

        await interaction.response.edit_message(view=self.view)

        await Stories.tell_story(
            bot=self.bot,
            guide=self.guide,
            thread=self.thread,
            reader_user=self.reader_user,
            story=self.story,
            to_id=self.to_id
        )

class StoryLine:
    def __init__(self, type, content):
        self.type = type
        self.content = content


class StoryNodeInfo:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Story:
    def __init__(self, title=None, description=None, author=None, image=None, emoji=None, date=None, node=None):
        self.title = title
        self.description = description
        self.author = author
        self.image = image
        self.emoji = emoji
        self.date = date
        self.node = node


# from https://stackoverflow.com/a/68331641/14351818
def get_story_from_lines(raw_contents):
    file_contents = []
    story = Story()
    for line in raw_contents:
        new_line: str = line
        new_line = new_line.replace("<n>", "\n")
        new_line = new_line.replace("<aheze>", "<@743230678795288637>")
        
        if new_line.startswith("title:"):
            story.title = new_line.removeprefix("title:").strip()
        elif new_line.startswith("description:"):
            story.description = new_line.removeprefix("description:").strip()
        elif new_line.startswith("author:"):
            story.author = new_line.removeprefix("author:").strip()
        elif new_line.startswith("image:"):
            story.image = new_line.removeprefix("image:").strip()
        elif new_line.startswith("emoji:"):
            story.emoji = new_line.removeprefix("emoji:").strip()
        elif new_line.startswith("date:"):
            date_string = new_line.removeprefix("date:").strip()
            date = datetime.strptime(date_string, TIME_FORMATTING) 
            story.date = date
        else:
            file_contents.append(new_line)
        

    # initialize stack with the root node, also remove first line
    root_node = Node("0<->StoryRootNode")
    stack = {0: root_node}

    for index, line in enumerate(file_contents):
        leading_spaces = len(line) - len(line.lstrip('    '))
        indent = int(leading_spaces / 4) + 1 # indent = 3 spaces
        string = f"{index + 1}<->{line}"

            # add the node to the stack, set as parent the node that's one level up
        stack[indent] = Node(string, parent=stack[indent - 1])
        
    tree = stack[0]
    story.node = tree

    return story


def parse_file():
    stories = []
    with open('Config/Stories.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        # 0: rate
        # 1: How to rate the app
        # 2: First, open...
        # 3: Then......
        current_story = []
        for line in file_contents:
            story_line = line
            if line.startswith("title:"):
                current_story = []
                stories.append(current_story)
            current_story.append(story_line)

    print(stories)
    return stories

