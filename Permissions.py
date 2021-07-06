MOD_ID = "859636240978673715"
ADMIN_ID = "743230678795288637"


def check_no_permissions(author):
    role_ids = [str(role.id) for role in author.roles]
    return MOD_ID not in role_ids and str(author.id) != ADMIN_ID

def check_no_admin_permissions(author):
    role_ids = [str(role.id) for role in author.roles]
    return str(author.id) != ADMIN_ID