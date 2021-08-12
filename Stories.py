
from anytree.render import RenderTree
from dotenv.compat import to_env
import StoriesBase
import discord
import asyncio
from anytree import Node, search

def get_node_info(node):
    node_name = node.name.split("<->")
    id = int(node_name[0])
    name = node_name[1].strip()

    node_id_name = StoriesBase.StoryNodeInfo(id=id, name=name)
    return node_id_name

def is_quote(node_name: str):
    return node_name.startswith(">")

def strip_quote(node_name: str):
    stripped = node_name.removeprefix(">").strip()
    return stripped

async def end(guide, thread):
    embed = discord.Embed(title="The End", description="You've made it to the end of the story!")
    guide_guild = guide.get_guild(thread.guild.id)
    guide_thread  = guide_guild.get_thread(thread.id)
    await guide_thread.send(embed=embed)

async def choose_story(bot, guide, ctx):
    stories = StoriesBase.parse_file()
    parsed_stories = []

    for story in stories:
        parsed_story = StoriesBase.get_story_from_lines(story)
        parsed_stories.append(parsed_story)
        
    embed = discord.Embed(title="Choose a story!", description=f"Click the dropdown menu to select a story, then press the `Start` button!", color=0x00aeef)
    view = StoriesBase.StoryDropdownChooserView(bot, guide, ctx.channel, parsed_stories)
    await ctx.send(embed=embed, view=view)

async def start_story(bot, guide, channel, embed_message, story, to_id=1):
    new_thread = await channel.start_thread(name=story.title, message=embed_message, type=discord.ChannelType.public_thread)
    guide_guild = guide.get_guild(new_thread.guild.id)
    guide_thread = guide_guild.get_thread(new_thread.id)
    await guide_thread.join()
    await tell_story(
        bot=bot,
        guide=guide,
        thread=new_thread,
        story=story,
        to_id=to_id
    )

async def tell_story(bot, guide, thread, story, to_id=1):
    if to_id == -200:
        await end(guide, thread)
        return

    next_quotes, next_button_infos = jump_to(story.node, to_id)

    if len(next_quotes) <= 1 and len(next_button_infos) == 0:
        await end(guide, thread)
        return

    for next_quote in next_quotes:
        if next_quote.type == "quote":
            async with thread.typing():
                length = len(next_quote.content)
                duration = length * 0.05
                print(duration)
                await asyncio.sleep(duration)
                await thread.send(next_quote.content)

    view = StoriesBase.StoryButtonView(
        bot=bot,
        guide=guide,
        thread=thread,
        story=story,
        next_button_infos=next_button_infos
    )

    embed = discord.Embed(description="<a:Progress:863079541675917402>")
    guide_guild = guide.get_guild(thread.guild.id)
    guide_thread = guide_guild.get_thread(thread.id)
    message = await guide_thread.send(embed=embed, view=view)
    await message.edit(suppress=True)


def jump_to(tree, node_id):
    # tree = StoriesBase.parse_tree()
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
            line = StoriesBase.StoryLine(type="quote", content=stripped_quote)
            next_quotes.append(line)

            if len(sibling_node.children) > 0: # a button now!
                if len(sibling_node.children) == 1: # 1 button, keep going

                    button_node = sibling_node.children[0]
                    button_node_info = get_node_info(button_node)  
                    
                    next_index = index + 1
                    if len(sibling_nodes) > next_index:
                        next_node = sibling_nodes[next_index]
                        next_node_info = get_node_info(next_node)  

                        next_button_info = StoriesBase.StoryNodeInfo(id=next_node_info.id, name=button_node_info.name)
                        next_button_infos.append(next_button_info)
                    else:
                        next_button_info = StoriesBase.StoryNodeInfo(id=-200, name=button_node_info.name)

                else: # 2 buttons or more
                    for button_node in sibling_node.children:
                        button_node_info = get_node_info(button_node)  

                        if len(button_node.children) > 0: # travel down
                            first_quote = button_node.children[0]
                            first_quote_info = get_node_info(first_quote)  
                            next_button_info = StoriesBase.StoryNodeInfo(id=first_quote_info.id, name=button_node_info.name)
                            next_button_infos.append(next_button_info)
                        else: # keep going to next sibling
                            siblings_including_self = button_node.parent.children
                            current_node_index_in_siblings = siblings_including_self.index(button_node)
                            next_button_node_index = current_node_index_in_siblings + 1

                            if len(siblings_including_self) > next_button_node_index:
                                next_node = siblings_including_self[next_button_node_index]
                                next_node_info = get_node_info(next_node)  

                                next_button_info = StoriesBase.StoryNodeInfo(id=next_node_info.id, name=button_node_info.name)
                                next_button_infos.append(next_button_info)
                            else:
                                next_button_info = StoriesBase.StoryNodeInfo(id=-200, name=button_node_info.name)
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

                next_button_info = StoriesBase.StoryNodeInfo(id=next_node_info.id, name=current_node_info.name)
                next_button_infos.append(next_button_info)
            else: # last single-button in a row
                
                parent = current_node.parent
                parent_siblings_including_parent = parent.parent.children
                parent_node_index_in_siblings = parent_siblings_including_parent.index(parent)
                next_node_index = parent_node_index_in_siblings + 1

                if len(parent_siblings_including_parent) > next_node_index:
                    next_node = parent_siblings_including_parent[next_node_index]
                    next_node_info = get_node_info(next_node) 
                     
                    next_button_info = StoriesBase.StoryNodeInfo(id=next_node_info.id, name=current_node_info.name)
                    next_button_infos.append(next_button_info)

                else:
                    print("Last button. End.")

        else:
            print("Current button node has no siblings, should not have been directed to this node")



    # print(f"Next quotes: {[ quote.__dict__ for quote in next_quotes ]}")
    print(f"Next button infos: {[ info.__dict__ for info in next_button_infos ]}")

    return (next_quotes, next_button_infos)