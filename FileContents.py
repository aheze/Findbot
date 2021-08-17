import pathlib


def server_path(guild_id, file_path):
    guild_folder_path = f"ServerSpecific/{guild_id}"
    path = pathlib.Path(guild_folder_path)
    server_file_path = path / file_path
    return server_file_path

def get_file_contents(file):
    raw_lines = list(filter(None, file.readlines()))
    file_contents = [x.rstrip() for x in raw_lines if x.rstrip()]
    return file_contents

# combine into a single str
def combine_file_contents(file_contents):
    new_file_contents = [line.strip() for line in file_contents]
    combined = "\n".join(new_file_contents)
    combined += "\n"
    if combined == "\n":
        combined = ""
    return combined
