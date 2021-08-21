import FileContents

def get_roles_from_storage(guild_id, user_id):
    saved_roles_file = FileContents.server_path(guild_id, "Storage/SavedRoles.txt")
    new_file_contents = []
    roles = []
    with open(saved_roles_file, 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        for line in file_contents:
            components = line.strip().split(":")  # 0 is time, 1 is action
            if not str(user_id) in components[0]:
                new_file_contents.append(line)
            else:
                roles = components[1].split(",")

    with open(saved_roles_file, 'w') as file:
        combined=FileContents.combine_file_contents(new_file_contents)
        file.write(combined)

    return roles

def save_roles_to_storage(guild_id, user_id, roles):
    saved_roles_file = FileContents.server_path(guild_id, "Storage/SavedRoles.txt")
    with open(saved_roles_file, 'a') as file:
        string=f"{user_id}:{roles}\n"
        file.write(string)
