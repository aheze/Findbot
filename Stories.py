import StoriesBase
from anytree import Node, search

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


async def story(bot, ctx, args):
    print("called")
    combined = "".join(args).strip()
    next_quotes, next_button_infos = jump_to(1)

    print("got!")
    print(next_quotes)
    for next_quote in next_quotes:
        print(next_quote)
        await ctx.send(next_quote)






def jump_to(node_id):
    tree = StoriesBase.parse_tree()
    nodes = search.findall(tree, lambda node: f"{node_id}<->" in node.name)
    if len(nodes) == 0:
        print("DIDN'T FIND NODE.")
        return

    current_node: Node = nodes[0]

    print(f"Current Node ID ({node_id}) name: {current_node.name}")
    current_node_info = get_node_info(current_node)  

    next_quotes = [] # first, loop over quotes
    next_button_infos = [] # then, loop over buttons

    if is_quote(current_node_info.name): # current node is a quote, continue through siblings
        sibling_nodes = [current_node]
        sibling_nodes += current_node.siblings

        for (index, sibling_node) in enumerate(sibling_nodes):
            sibling_node_info = get_node_info(sibling_node)
            stripped_quote = strip_quote(sibling_node_info.name)
            next_quotes.append(stripped_quote)

            if len(sibling_node.children) > 0: # a button now!
                if len(sibling_node.children) == 1: # 1 button, keep going
                    print("1 button")

                    button_node = sibling_node.children[0]
                    button_node_info = get_node_info(button_node)  
                    
                    next_index = index + 1
                    if len(sibling_nodes) > next_index:
                        next_node = sibling_nodes[next_index]
                        next_node_info = get_node_info(next_node)  

                        next_button_info = StoryNodeInfo(id=next_node_info.id, name=button_node_info.name)
                        next_button_infos.append(next_button_info)
                    else:
                        print("OUT OF RANGE")

                else: # 2 buttons or more
                    for button_node in sibling_node.children:
                        print(f"Sibling child nodes: {button_node}")
                        button_node_info = get_node_info(button_node)  

                        if len(button_node.children) > 0: # travel down
                            first_quote = button_node.children[0]
                            first_quote_info = get_node_info(first_quote)  
                            next_button_info = StoryNodeInfo(id=first_quote_info.id, name=button_node_info.name)
                            next_button_infos.append(next_button_info)
                        else: # keep going to next sibling
                            # button_node = sibling_node.children[0]
                            # button_node_info = get_node_info(button_node)  

                            siblings_including_self = button_node.parent.children
                            current_node_index_in_siblings = siblings_including_self.index(button_node)
                            next_button_node_index = current_node_index_in_siblings + 1
                            print(f"Next index: {next_button_node_index}")

                            next_node = siblings_including_self[next_button_node_index]
                            next_node_info = get_node_info(next_node)  

                            next_button_info = StoryNodeInfo(id=next_node_info.id, name=button_node_info.name)
                            next_button_infos.append(next_button_info)

                            break
                            
                            # next_index = index + 1
                            # if len(sibling_nodes) > next_index:
                            #     next_node = sibling_nodes[next_index]
                            #     next_node_info = get_node_info(next_node)  

                            #     next_button_info = StoryNodeInfo(id=next_node_info.id, name=button_node_info.name)
                            #     next_button_infos.append(next_button_info)
                            # else:
                            #     print("OUT OF RANGE")
                break
    else:
        print("current is button")
        if len(current_node.siblings) > 0: # multiple single-button in a row
            # next_node_info = get_node_info(next_node) 
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

                print(f"parent node's index: {parent_node_index_in_siblings}")

                if len(parent_siblings_including_parent) > next_node_index:
                    next_node = parent_siblings_including_parent[next_node_index]
                    next_node_info = get_node_info(next_node) 
                     
                    next_button_info = StoryNodeInfo(id=next_node_info.id, name=current_node_info.name)
                    next_button_infos.append(next_button_info)

                else:
                    print("Last button. End.")

        else:
            print("Current button node has no siblings, should not have been directed to this node")




    print(f"Next quotes: {next_quotes}")
    print(f"Next button infos: {[ info.__dict__ for info in next_button_infos ]}")

    return (next_quotes, next_button_infos)
                    # print(f"BUTTON id name: {button_node_id_name.__dict__}")    
            # child_name = sibling_node_id_name.name # keep the name


            # to_id = 

# jump_to(4)

    # if current_node.name == "0<->StoryRootNode" or len(current_node.children) > 1: # start, or has many children
    #     print("yep!")
    #     for child in current_node.children:
    #         child_id_name = get_node_info(child)
    #         print(f"Child id name: {child_id_name.__dict__}")
    #         print(child_id_name.name)
    #         if is_quote(child_id_name.name):
    #             print("is quote!")
    #             stripped_quote = strip_quote(child_id_name.name)
    #             next_quotes.append(stripped_quote)
    #         if len(child.children) > 0: # a button now!
    #             child_name = child_id_name.name # keep the name
                

    #             next_button_id_names.append(child_id_name)
    #             break

            # child_id_name = get_node_info(child)
            # print(f"Child id name: {child_id_name.__dict__}")
            # if is_quote(child_id_name.name):
            #     stripped_quote = strip_quote(child_id_name.name)
            #     next_quotes.append(stripped_quote)
            # else: # a button now!
            #     next_button_id_names.append(child_id_name)
    # else: # continue down 1 level
    #     sole_child: Node = current_node.children[0]

    #     if is_quote(sole_child.name):
    #         print(f"Error. Should not be quote here: {sole_child.name}")
    #     else: # child name is the name of the continue button
    #         child_id_name = get_node_info(sole_child)
    #         next_button_id_names.append(child_id_name)


    
    # for child in node.children:
    #     print(f"    child: {child.name}")


