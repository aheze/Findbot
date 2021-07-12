
async def determine_action(bot, server, channel, message, session_user_id, existing_message_string, node_name):
    action = node_name.removeprefix("<a>")
    print(f".{action}.")

    if action == "color":
        color_message = "Press color!"
        message_string = full_message(existing_message_string, color_message)
        await message.edit(content=message_string)


def full_message(existing_message_string, new_message_string):
    new_message_string = f"{existing_message_string}{new_message_string}\n*Thank you!*"
    return new_message_string