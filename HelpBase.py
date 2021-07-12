
import FileContents
from anytree import Node, RenderTree
import random

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

    emoji_split = emoji_name.split("/")
    if len(emoji_split) > 1:
        if selected:
            emoji_name = emoji_split[0]
        else:
            emoji_name = emoji_split[1]

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

    



