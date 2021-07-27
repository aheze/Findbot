
import FileContents
import Utilities
from anytree import Node, search
import re

# from https://stackoverflow.com/a/68331641/14351818
def parse_tree():
    with open('y_Help.txt', 'r') as file:
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
            indent = int(leading_spaces / 3) # indent = 3 spaces

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

def toggle_emoji(emoji_name, selected_emoji_name):
    opposite = emoji_name

    if emoji_name == "Currently_Unavailable":
        opposite = emoji_name 
    elif len(emoji_name) < 3:
        if selected_emoji_name == emoji_name:
            opposite = emoji_name.removesuffix("_") + "Selected"
    else:
        if selected_emoji_name not in emoji_name:
            opposite = emoji_name + "Unselected"
        

    return opposite

def replace_previous_with_unselected_emoji(bot, existing_text, except_selected_id):
    
    existing_split = existing_text.split("〰〰〰〰〰")
    previous_message = existing_split[-1]

    p = re.compile("\<:.+\>")
    result = p.findall(previous_message)

    for emoji_result in result:
        emoji_split = emoji_result.removeprefix("<:").split(":")
        emoji_name = emoji_split[0]
        selected_emoji = Utilities.get_emoji_from_id(bot, int(except_selected_id))

        if selected_emoji.name == "BotCommands":
            previous_message = previous_message.replace("Bot Commands", "__**B**__ot Commands")
        if selected_emoji.name == "ServerInformation":
            previous_message = previous_message.replace("Server Information", "Server __**I**__nformation")
        if selected_emoji.name == "StatsChart":
            previous_message = previous_message.replace("Server/App Stats", "Server/App __**S**__tats")
        if selected_emoji.name == "RoleInformation":
            previous_message = previous_message.replace("Role Information", "__**R**__ole Information")
        if selected_emoji.name == "CustomQuestion":
            previous_message = previous_message.replace("Ask a custom question", "__**A**__sk a custom question")

        new_name = toggle_emoji(emoji_name, selected_emoji.name)
        new_emoji = Utilities.get_emoji(bot, new_name)

        previous_message = previous_message.replace(str(emoji_result), f"{new_emoji}")

    new_split = existing_split
    new_split[-1] = previous_message

    return "〰〰〰〰〰".join(new_split)

def get_letter_id(node):
    name_split = node.name.split("<->")
    id = name_split[0]
    name = name_split[1]
    full_split = name.split("::", 1)

    letter_id = ""
    emoji_section = full_split[0].split(")")
    if len(emoji_section) > 1:
        letter_id = emoji_section[1]
    else:
        letter_id = emoji_section[0]
    return letter_id

def jump_to_node(letter_id):
    topic_tree = parse_tree()
    target_id = letter_id.upper()

    current_node = topic_tree
    for char in target_id:
        searching = True
        current_loop = 0
        while searching:
            for node in current_node.children:
                letter_id = get_letter_id(node)
                # print(f"ID: {letter_id}")
                if letter_id == char:
                    # print("same!")
                    current_node = node
            current_loop += 1
            if current_loop > 20:
                searching = False

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
    else:
        if not emoji_selected:
            emoji_name += "Unselected"

    topic_split = full_split[1].split("~~")

    if len(topic_split) < 2:
        # tuple = (emoji_name, topic_split[0], "", id)
        return NodeInformation(
            emoji_name=emoji_name,
            options_name=topic_split[0],
            selected_header_name="",
            digit_id=id
        )
    else:
        # tuple = (emoji_name, topic_split[0], topic_split[1], id)
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



    



