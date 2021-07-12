
def determine_action(bot, server, channel, message, session_user_id, existing_message_string, node_name):
    print("deter!")
    print(node_name)
    action = node_name.removeprefix("<a>")
    print(action)
