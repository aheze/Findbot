import Stats

def determine_action(bot, server, channel, node_name):
    action = node_name.removeprefix("<a>")

    if action == "members":
        member_count = server.member_count
        boosters_count = server.premium_subscription_count
        Stats.render_image()
        return ""

    return "Weird, please ping <@743230678795288637>"