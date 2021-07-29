import FileContents

def get_roles_from_storage(user_id):
    new_file_contents = []
    roles = []
    with open('Output/SavedRoles.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        for line in file_contents:
            components = line.strip().split(":")  # 0 is time, 1 is action
            if not str(user_id) in components[0]:
                new_file_contents.append(line)
            else:
                roles = components[1].split(",")

    with open('Output/SavedRoles.txt', 'w') as file:
        combined=FileContents.combine_file_contents(new_file_contents)
        file.write(combined)

    return roles

def save_roles_to_storage(user_id, roles):
    with open('Output/SavedRoles.txt', 'a') as file:
        string=f"{user_id}:{roles}\n"
        file.write(string)
