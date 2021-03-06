
import FileContents
import Utilities
from anytree import Node, search
import re

# from https://stackoverflow.com/a/68331641/14351818
def parse_tree(guild_id):
    help_file = FileContents.server_path(guild_id, "Config/Help.txt")

    with open(help_file, 'r') as file:
        raw_contents = FileContents.get_file_contents(file)
        if len(raw_contents) == 0:
            help_file = "ServerShared/Config/Help.txt"

    with open(help_file, 'r') as file:
        raw_contents = FileContents.get_file_contents(file)

        file_contents = []
        
        for line in raw_contents:
            new_line = line
            new_line = new_line.replace("<n>", "\n")
            new_line = new_line.replace("<aheze>", "<@743230678795288637>")
            file_contents.append(new_line)

        # initialize stack with the root node, also remove first line
        stack = {0: Node(file_contents.pop(0))}

        for index, line in enumerate(file_contents):
            leading_spaces = len(line) - len(line.lstrip(' '))
            indent = int(leading_spaces / 4) # indent = 4 spaces
            emoji_split = line.split("::")
            if len(emoji_split) < 2:
                children = stack[indent-1].children
                children_count = len(children) + 1
                letter = chr(ord('@') + children_count)
                line_string = f"{index}<->{letter}::{line.strip()}"
            else:
                line_string = f"{index}<->{line.strip()}"

            # add the node to the stack, set as parent the node that's one level up
            stack[indent] = Node(line_string, parent=stack[indent-1])
            
        tree = stack[0]
        return tree

def sub_server_stats(string, server):
    if "<member_count>" in string:
        string = string.replace("<member_count>", f"{server.member_count}")
    if "<boosters_count>" in string:
        string = string.replace("<boosters_count>", f"{server.premium_subscription_count}")
        if server.premium_subscription_count == 1:
            string = string.replace("boosters", f"booster")

    return string

def toggle_emoji(emoji_name, selected_emoji_name):
    opposite = emoji_name

    if emoji_name == "Currently_Unavailable":
        opposite = emoji_name 
    elif len(emoji_name) < 3:
        if selected_emoji_name == emoji_name:
            opposite = emoji_name.removesuffix("_") + "Selected"
    else:
        if selected_emoji_name == emoji_name:
            opposite = emoji_name + "Selected"
        
    return opposite

def replace_previous_with_unselected_emoji(bot, existing_text, except_selected_id):
    existing_split = existing_text.split("???????????????")
    previous_message = existing_split[-1]

    p = re.compile("\<:.+\>")
    result = p.findall(previous_message)

    selected_emoji = Utilities.get_specific_emoji_from_id(bot, [871866926173921320, 871866989294006382], int(except_selected_id))

    for emoji_result in result:
        emoji_split = emoji_result.removeprefix("<:").split(":")
        emoji_name = emoji_split[0]

        if "Commands" in selected_emoji.name:
            previous_message = previous_message.replace("Bot Commands", "__**B**__ot Commands")
        if "Info" in selected_emoji.name:
            previous_message = previous_message.replace("Server Information", "Server __**I**__nformation")
        if "Stats" in selected_emoji.name:
            previous_message = previous_message.replace("Server/App Stats", "Server/App __**S**__tats")
        if "Roles" in selected_emoji.name:
            previous_message = previous_message.replace("Role Information", "__**R**__ole Information")
        if "Help" in selected_emoji.name:
            previous_message = previous_message.replace("Ask a custom question", "__**A**__sk a custom question")
        # if "Settings" in selected_emoji.name:
        #     previous_message = previous_message.replace("Settings", "S")

        
        new_name = toggle_emoji(emoji_name, selected_emoji.name)
        new_emoji = Utilities.get_specific_emoji(bot, [871866926173921320, 871866989294006382], new_name)

        previous_message = previous_message.replace(str(emoji_result), f"{new_emoji}")

    new_split = existing_split
    new_split[-1] = previous_message

    return "???????????????".join(new_split)

def get_letter_id(node):
    name_split = node.name.split("<->")
    name = name_split[1]
    full_split = name.split("::", 1)

    letter_id = ""
    emoji_section = full_split[0].split(")")
    if len(emoji_section) > 1:
        letter_id = emoji_section[1]
    else:
        letter_id = emoji_section[0]
    return letter_id

def jump_to_node(guild_id, letter_id):
    topic_tree = parse_tree(guild_id)
    target_id = letter_id.upper()

    current_node = topic_tree
    for char in target_id:
        for node in current_node.children:
            letter_id = get_letter_id(node)
            if letter_id == char:
                current_node = node
                break

    return current_node

def generate_identifier_for_node(node: Node):

    ancestors = list(node.ancestors)
    ancestors.pop(0)
    ancestors.append(node)

    path = ""

    for ancestor in ancestors:
        letter_id = get_letter_id(ancestor)
        path += letter_id

    return path

class NodeInformation:
    def __init__(self, emoji_name, options_name, selected_header_name, digit_id):
        self.emoji_name = emoji_name
        self.options_name = options_name
        self.selected_header_name = selected_header_name 
        self.digit_id = digit_id 

def get_node_info(node, emoji_selected: bool = True):
    name_split = node.name.split("<->")
    if len(name_split) == 1:
        return
        
    id = name_split[0]
    name = name_split[1]

    full_split = name.split("::", 1)
    emoji_section = full_split[0].split(")")
    emoji_name = emoji_section[0]

    if emoji_name == "Currently_Unavailable":
        pass
    elif len(emoji_name) < 2:
        if emoji_selected:
            emoji_name += "Selected"
        else:
            emoji_name += "_"

    topic_split = full_split[1].split("~~")

    if len(topic_split) < 2:
        return NodeInformation(
            emoji_name=emoji_name,
            options_name=topic_split[0],
            selected_header_name="",
            digit_id=id
        )
    else:
        return NodeInformation(
            emoji_name=emoji_name,
            options_name=topic_split[0],
            selected_header_name=topic_split[1],
            digit_id=id
        )

def get_child_node_infos(tree, selected_emoji_version):
    node_infos = []
    for topic in tree.children:
        node_info = get_node_info(topic, selected_emoji_version)
        node_infos.append(node_info)

    return node_infos



    



