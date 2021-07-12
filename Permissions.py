MOD_ID = 859636240978673715
ADMIN_ID = 743230678795288637

FINDBOT_ID = 784531493204262942
FINDBOT_TEST_ID = 860667927345496075


def check_no_permissions(author):
    role_ids = [role.id for role in author.roles]
    return MOD_ID not in role_ids and author.id != ADMIN_ID

def check_no_admin_permissions(author):
    return author.id != ADMIN_ID

def check_is_bot(author):
    return author.id == FINDBOT_ID or author.id == FINDBOT_TEST_ID