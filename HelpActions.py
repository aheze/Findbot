import Stats

def determine_action(node_name):
    action_split = node_name.split("<a>")
    action = action_split[1]
    
    if action == "members":
        chart_config = Stats.StatChartConfig(
            log_file_path="Logs/ServerMembersLog.txt",
            y_axis_name="Server Members",
            color_tuple=(96, 181, 255)
        )
        url = Stats.render_stats_image(chart_config)
        return url
    elif action == "boosters":
        chart_config = Stats.StatChartConfig(
            log_file_path="Logs/ServerBoostersLog.txt",
            y_axis_name="Server Boosters",
            color_tuple=(244, 127, 255)
        )
        url = Stats.render_stats_image(chart_config)
        return url
    return "Weird, please ping <@743230678795288637>"