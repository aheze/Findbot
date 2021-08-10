import FileContents
from anytree import Node, RenderTree, search

# from https://stackoverflow.com/a/68331641/14351818
def parse_tree():
    with open('Config/Stories.txt', 'r') as file:
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