
import FileContents
import Utilities
from anytree import Node, RenderTree
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


            # line = line_string

            
                # print(f"{children_count} in {stack[indent-1].name}")
            
            print(f"{line_string}\n")
            stack[indent] = Node(line_string, parent=stack[indent-1])
            
            
            # print(f"Stack {stack[indent].name}: {len(stack[indent].siblings)}\n")
    # print(f"Stack {stack[indent-1].name}: {len(stack[indent-1].siblings)}\n")
        tree = stack[0]
        return tree

parse_tree()

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
        new_name = toggle_emoji(emoji_name, selected_emoji.name)
        new_emoji = Utilities.get_emoji(bot, new_name)

        previous_message = previous_message.replace(str(emoji_result), f"{new_emoji}")

    new_split = existing_split
    new_split[-1] = previous_message

    return "〰〰〰〰〰".join(new_split)

def get_name_for(node, selected: bool = True):
    print("Get name!")
    name_split = node.name.split("<->")
    id = name_split[0]
    name = name_split[1]

    full_split = name.split("::", 1)
    emoji_name = full_split[0]

    if emoji_name == "Currently_Unavailable":
        pass
    elif len(emoji_name) < 2:
        if selected:
            emoji_name += "Selected"
        else:
            emoji_name += "_"
    else:
        if not selected:
            emoji_name += "Unselected"


    print(emoji_name)

    topic_split = full_split[1].split("~~")

    if len(topic_split) < 2:
        tuple = (emoji_name, topic_split[0], "", id)
    else:
        tuple = (emoji_name, topic_split[0], topic_split[1], id)
        
    return tuple

def get_topics_for(tree, selected_emoji_version):
    tuples = []
    for topic in tree.children:
        tuple = get_name_for(topic, selected_emoji_version)
        tuples.append(tuple)

    return tuples



    



