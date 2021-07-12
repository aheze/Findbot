import FileContents
import discord

def get_roles_from_storage(user_id):
    print("getting roles")
    new_file_contents = []
    roles = []
    with open('z_SavedRoles.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        for line in file_contents:
            components = line.strip().split(":")  # 0 is time, 1 is action
            if not str(user_id) in components[0]:
                new_file_contents.append(line)
            else:
                roles = components[1].split(",")

    with open('z_SavedRoles.txt', 'w') as file:
        combined=FileContents.combine_file_contents(new_file_contents)
        file.write(combined)

    return roles

def save_roles_to_storage(user_id, roles):
    print("saving roles")
    with open('z_SavedRoles.txt', 'a') as file:
        string=f"{user_id}:{roles}\n"
        file.write(string)
