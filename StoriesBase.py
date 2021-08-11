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
        root_node = Node("0<->StoryRootNode")
        stack = {0: root_node}

        for index, line in enumerate(file_contents):
            leading_spaces = len(line) - len(line.lstrip('    '))
            indent = int(leading_spaces / 4) + 1 # indent = 3 spaces
            string = f"{index + 1}<->{line}"

             # add the node to the stack, set as parent the node that's one level up
            stack[indent] = Node(string, parent=stack[indent - 1])
            
        tree = stack[0]

        return tree