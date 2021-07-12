
from anytree import Node, RenderTree

# from https://stackoverflow.com/a/68331641/14351818
def parse_tree():
    with open('y_Help.txt', 'r') as file:
        raw_lines = list(filter(None, file.readlines()))
        file_contents = [x.rstrip() for x in raw_lines if x.rstrip()]

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

def get_name_for(node):
    name_split = node.name.split("<->")
    id = name_split[0]
    name = name_split[1]

    topic_split = name.split("~~")
    emoji_name = topic_split[0]
    options_display_name = topic_split[1]
    title_name = topic_split[2]

    tuple = (emoji_name, options_display_name, title_name, id)
    return tuple

def get_topics_for(tree):
    tuples = []
    for topic in tree.children:
        tuple = get_name_for(topic)
        tuples.append(tuple)

    return tuples

    # path_array = [node.name for node in topic.path]
    #     path_string = "".join(path_array)
    #     print(path_string)
    



