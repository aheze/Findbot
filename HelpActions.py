import Stats

def determine_action(bot, server, channel, node_name):
    action = node_name.removeprefix("<a>")

    if action == "members":
        Stats.render_image()
        return ""

    return "Weird, please ping <@743230678795288637>"