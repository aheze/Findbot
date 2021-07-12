
import FileContents
import Utilities
from anytree import Node, RenderTree
import random
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

            line_string = f"{index}<->{line.strip()}"

            # add the node to the stack, set as parent the node that's one level up
            stack[indent] = Node(line_string, parent=stack[indent-1])

        tree = stack[0]
        return tree

parse_tree()

def generate_selected_emoji_pairs(emoji_name):
    opposite = None
    if len(emoji_name) < 3:
        opposite = emoji_name.removesuffix("_") + "Selected"

    else:
        if "Unselected" in emoji_name:
            opposite = emoji_name.removesuffix("Unselected")
        else:
            opposite = emoji_name + "Unselected"

    print(f"Opposite: {opposite}")
    return opposite
    

# <:BotCommands:864010866051121152>


def replace_previous_with_unselected_emoji(bot, existing_text, except_selected_id):
    print("replace!!")
    existing_split = existing_text.split("〰〰〰〰〰")
    previous_message = existing_split[-1]

    p = re.compile("\<:.+\>")
    result = p.findall(previous_message)


    for emoji_result in result:
        emoji_split = emoji_result.removeprefix("<:").split(":")
        # print(f"SPLIT {emoji_split}")
        emoji_name = emoji_split[0]
        # print(f"Name: {emoji_name}")

        new_name = generate_selected_emoji_pairs(emoji_name)
        # print("Name..")
        # print(new_name)
        new_emoji = Utilities.get_emoji(bot, new_name)
        # print("New:")
        # print(new_emoji)

        print(f"Res.. {emoji_result}")
        print(f"new_emoji.. {new_emoji}")
        print("prev 1...")
        print(previous_message)
        previous_message = previous_message.replace(str(emoji_result), f"{new_emoji}")
        print("prev 2...")
        print(previous_message)

    print("prev...")
    print(previous_message)

    new_split = existing_split
    new_split[-1] = previous_message
    print("New......")
    print(new_split)


    # print(existing_split)
    # print(f"COUNTTT: {len(existing_split)}")
    return "〰〰〰〰〰".join(new_split)

def get_name_for(node, selected: bool = True):
    name_split = node.name.split("<->")
    id = name_split[0]
    name = name_split[1]

    topic_split = name.split("~~")
    emoji_name = topic_split[0]

    if len(emoji_name) < 2:
        if selected:
            emoji_name += "Selected"
        else:
            emoji_name += "_"

    else:
        if not selected:
            emoji_name += "Unselected"

    options_display_name = topic_split[1]
    title_name = topic_split[2]

    tuple = (emoji_name, options_display_name, title_name, id)
    return tuple

def get_topics_for(tree, selected_emoji_version):
    tuples = []
    for topic in tree.children:
        tuple = get_name_for(topic, selected_emoji_version)
        tuples.append(tuple)

    return tuples

def random_greeting(user_mention):
    with open('y_HelpGreetings.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
        greeting = random.choice(file_contents)
        message_string = greeting.replace("<m>", user_mention)
        return message_string

    



