import Stats

def determine_action(node_name):
    action = node_name.removeprefix("<a>")

    if action == "members":
        chart_config = Stats.StatChartConfig(
            log_file_path="Output/Logs/ServerMembersLog.txt",
            output_file_name="ServerMembers",
            y_axis_name="Server Members",
            color_tuple=(96, 181, 255)
        )
        url = Stats.render_stats_image(chart_config)
        return url
    elif action == "boosters":
        chart_config = Stats.StatChartConfig(
            log_file_path="Output/Logs/ServerBoostersLog.txt",
            output_file_name="ServerBoosters",
            y_axis_name="Server Boosters",
            color_tuple=(244, 127, 255)
        )
        url = Stats.render_stats_image(chart_config)
        return url
    return "Weird, please ping <@743230678795288637>"