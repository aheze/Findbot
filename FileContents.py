
def get_file_contents(file):
    raw_lines = list(filter(None, file.readlines()))
    file_contents = [x.rstrip() for x in raw_lines if x.rstrip()]
    return file_contents

# combine into a single str
def combine_file_contents(file_contents):
    combined = "\n".join(file_contents)
    combined += "\n"
    if combined == "\n":
        combined = ""
    return combined
