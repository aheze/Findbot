import FileContents
import Stories
import discord
from anytree import Node, RenderTree, search

class StoryChooserButton(discord.ui.Button):
    def __init__(self, bot, guide, channel, story):
        super().__init__(label="Start", style=discord.ButtonStyle.green)
        
        self.bot = bot
        self.guide = guide
        self.channel = channel
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
            embed_message=interaction.message,
            story=self.story
        )

class StoryChooserDropdown(discord.ui.Select):
    def __init__(self, bot, guide, thread, stories, selected_story_index=None):

        self.bot = bot
        self.guide = guide
        self.thread = thread
        self.stories = stories

        options = []
        for index, story in enumerate(stories):
            if selected_story_index is not None:
                if selected_story_index == index:
                    option = discord.SelectOption(label=story.title, description=f"By {story.author}", default=True)
                else:   
                    option = discord.SelectOption(label=story.title, description=f"By {story.author}")
            else:
                option = discord.SelectOption(label=story.title, description=f"By {story.author}")
            options.append(option)
        
        super().__init__(placeholder='Choose a story', options=options)

    async def callback(self, interaction: discord.Interaction):
        print(f"Called! {self.values[0]}")

        # selected_story = self.stories.first
        for index, story in enumerate(self.stories):
            if story.title == self.values[0]:
                break
        else:
            index = -1

        view = StoryDropdownChooserView(self.bot, self.guide, self.thread, self.stories, selected_story_index=index)
        story = self.stories[index]
        embed = discord.Embed(title=story.title, description=f"{story.description}", color=0x00aeef)
        embed.set_image(url=story.image)
        embed.set_footer(text=f"By {story.author}")
        await interaction.response.edit_message(embed=embed, view=view)

class StoryDropdownChooserView(discord.ui.View):
    selected_story = None
    def __init__(self, bot, guide, channel, stories, selected_story_index=None):
        super().__init__()

        self.add_item(StoryChooserDropdown(bot, guide, channel, stories, selected_story_index))
        if selected_story_index is not None:
            if len(stories) > selected_story_index:
                self.add_item(StoryChooserButton(bot, guide, channel, stories[selected_story_index]))
            else:
                self.add_item(StoryChooserButton(bot, guide, channel, None))
        else:
            self.add_item(StoryChooserButton(bot, guide, channel, None))

class StoryButtonView(discord.ui.View):
    session_message = None

    def __init__(self, bot, guide, thread, story, next_button_infos):
        super().__init__(timeout=None)
        self.bot = bot
        self.guide = guide
        self.thread = thread

        for next_button_info in next_button_infos:
            print(next_button_info.__dict__)
            self.add_item(
                StoryButton(
                    bot=bot,
                    guide=guide,
                    thread=thread,
                    story=story,
                    label=next_button_info.name,
                    to_id=next_button_info.id
                )
            )

class StoryButton(discord.ui.Button):
    def __init__(self, bot, guide, thread, story, label, to_id):
        super().__init__(label=label, style=discord.ButtonStyle.gray)
        self.bot = bot
        self.guide = guide
        self.thread = thread
        self.story = story
        self.label = label
        self.to_id = to_id

    async def callback(self, interaction: discord.Interaction):
        self.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view=self.view)

        await Stories.tell_story(
            bot=self.bot,
            guide=self.guide,
            thread=self.thread,
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
    def __init__(self, title=None, description=None, author=None, image=None, node=None):
        self.title = title
        self.description = description
        self.author = author
        self.image = image
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

