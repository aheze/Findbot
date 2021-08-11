
from dotenv.compat import to_env
import StoriesBase
import discord
import asyncio
from anytree import Node, search

class StoryButtonView(discord.ui.View):
    session_message = None

    def __init__(self, bot, guide, channel, next_button_infos):
        super().__init__(timeout=None)
        self.bot = bot
        self.guide = guide
        self.channel = channel

        for next_button_info in next_button_infos:
            print(next_button_info.__dict__)
            self.add_item(
                StoryButton(
                    bot=bot,
                    guide=guide,
                    channel=channel,
                    label=next_button_info.name,
                    to_id=next_button_info.id
                )
            )

class StoryButton(discord.ui.Button):
    def __init__(self, bot, guide, channel, label, to_id):
        super().__init__(label=label, style=discord.ButtonStyle.gray)
        self.bot = bot
        self.guide = guide
        self.channel = channel
        self.label = label
        self.to_id = to_id

    async def callback(self, interaction: discord.Interaction):
        self.style = discord.ButtonStyle.blurple
        await interaction.response.edit_message(view=self.view)

        await story(
            bot=self.bot,
            guide=self.guide,
            channel=self.channel,
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

def get_node_info(node):
    node_name = node.name.split("<->")
    id = int(node_name[0])
    name = node_name[1].strip()

    node_id_name = StoryNodeInfo(id=id, name=name)
    return node_id_name

def is_quote(node_name: str):
    return node_name.startswith(">")

def strip_quote(node_name: str):
    stripped = node_name.removeprefix(">").strip()
    return stripped

async def end(guide, channel):
    embed = discord.Embed(title="The End", description="You've made it to the end of the story!")
    guide_guild = guide.get_guild(channel.guild.id)
    guide_channel = guide_guild.get_channel(channel.id)
    await guide_channel.send(embed=embed)


async def story(bot, guide, channel, to_id=1):
    if to_id == -200:
        await end(guide, channel)
        return

    next_quotes, next_button_infos = jump_to(to_id)

    if len(next_quotes) <= 1 and len(next_button_infos) == 0:
        await end(guide, channel)
        return

    for next_quote in next_quotes:
        if next_quote.type == "quote":
            async with channel.typing():
                length = len(next_quote.content)
                duration = length * 0.05
                print(duration)
                await asyncio.sleep(duration)
                await channel.send(next_quote.content)

    view = StoryButtonView(
        bot=bot,
        guide=guide,
        channel=channel,
        next_button_infos=next_button_infos
    )

    embed = discord.Embed(description="<a:Progress:863079541675917402>")
    guide_guild = guide.get_guild(channel.guild.id)
    guide_channel = guide_guild.get_channel(channel.id)
    message = await guide_channel.send(embed=embed, view=view)
    await message.edit(suppress=True)



def jump_to(node_id):
    tree = StoriesBase.parse_tree()
    nodes = search.findall(tree, lambda node: f"{node_id}<->" in node.name)
    if len(nodes) == 0:
        print("DIDN'T FIND NODE.")
        return

    current_node: Node = nodes[0]

    current_node_info = get_node_info(current_node)  

    next_quotes = [] # first, loop over quotes
    next_button_infos = [] # then, loop over buttons

    if is_quote(current_node_info.name): # current node is a quote, continue through siblings
        sibling_nodes = current_node.parent.children
        current_node_index_in_sibling_nodes = sibling_nodes.index(current_node)
        sibling_nodes = sibling_nodes[current_node_index_in_sibling_nodes:]

        for (index, sibling_node) in enumerate(sibling_nodes):
            sibling_node_info = get_node_info(sibling_node)
            stripped_quote = strip_quote(sibling_node_info.name)
            line = StoryLine(type="quote", content=stripped_quote)
            next_quotes.append(line)

            if len(sibling_node.children) > 0: # a button now!
                if len(sibling_node.children) == 1: # 1 button, keep going

                    button_node = sibling_node.children[0]
                    button_node_info = get_node_info(button_node)  
                    
                    next_index = index + 1
                    if len(sibling_nodes) > next_index:
                        next_node = sibling_nodes[next_index]
                        next_node_info = get_node_info(next_node)  

                        next_button_info = StoryNodeInfo(id=next_node_info.id, name=button_node_info.name)
                        next_button_infos.append(next_button_info)
                    else:
                        next_button_info = StoryNodeInfo(id=-200, name=button_node_info.name)

                else: # 2 buttons or more
                    for button_node in sibling_node.children:
                        button_node_info = get_node_info(button_node)  

                        if len(button_node.children) > 0: # travel down
                            first_quote = button_node.children[0]
                            first_quote_info = get_node_info(first_quote)  
                            next_button_info = StoryNodeInfo(id=first_quote_info.id, name=button_node_info.name)
                            next_button_infos.append(next_button_info)
                        else: # keep going to next sibling
                            siblings_including_self = button_node.parent.children
                            current_node_index_in_siblings = siblings_including_self.index(button_node)
                            next_button_node_index = current_node_index_in_siblings + 1

                            if len(siblings_including_self) > next_button_node_index:
                                next_node = siblings_including_self[next_button_node_index]
                                next_node_info = get_node_info(next_node)  

                                next_button_info = StoryNodeInfo(id=next_node_info.id, name=button_node_info.name)
                                next_button_infos.append(next_button_info)
                            else:
                                next_button_info = StoryNodeInfo(id=-200, name=button_node_info.name)
                                next_button_infos.append(next_button_info)
                            break
                        
                break
    else:
        if len(current_node.siblings) > 0: # multiple single-button in a row
            siblings_including_self = current_node.parent.children
            current_node_index_in_siblings = siblings_including_self.index(current_node)
            next_button_node_index = current_node_index_in_siblings + 1

            if len(siblings_including_self) > next_button_node_index:
                next_node = siblings_including_self[next_button_node_index]
                next_node_info = get_node_info(next_node)  

                next_button_info = StoryNodeInfo(id=next_node_info.id, name=current_node_info.name)
                next_button_infos.append(next_button_info)
            else: # last single-button in a row
                
                parent = current_node.parent
                parent_siblings_including_parent = parent.parent.children
                parent_node_index_in_siblings = parent_siblings_including_parent.index(parent)
                next_node_index = parent_node_index_in_siblings + 1

                if len(parent_siblings_including_parent) > next_node_index:
                    next_node = parent_siblings_including_parent[next_node_index]
                    next_node_info = get_node_info(next_node) 
                     
                    next_button_info = StoryNodeInfo(id=next_node_info.id, name=current_node_info.name)
                    next_button_infos.append(next_button_info)

                else:
                    print("Last button. End.")

        else:
            print("Current button node has no siblings, should not have been directed to this node")



    # print(f"Next quotes: {[ quote.__dict__ for quote in next_quotes ]}")
    print(f"Next button infos: {[ info.__dict__ for info in next_button_infos ]}")

    return (next_quotes, next_button_infos)