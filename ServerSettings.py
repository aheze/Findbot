import FileContents
import json


def parse_json(guild_id):
    server_settings_file = FileContents.server_path(guild_id, "Storage/ServerConfig.txt")
    with open(server_settings_file, 'r') as file:
        data = json.load(file)
        return data

def settings(guild_id):
    json = parse_json(guild_id)
    return json



settings(807790675998277672)


