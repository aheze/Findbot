import Stats
import FileContents

def determine_action(guild_id, node_name):
    action_split = node_name.split("<a>")
    action = action_split[1]
    
    if action == "members":
        path = FileContents.server_path(guild_id, "Logs/ServerMembers.txt")
        chart_config = Stats.StatChartConfig(
            log_file_path=path,
            y_axis_name="Server Members",
            color_tuple=(96, 181, 255)
        )
        url = Stats.render_stats_image(chart_config)
        return url
    elif action == "boosters":
        path = FileContents.server_path(guild_id, "Logs/ServerBoosters.txt")
        chart_config = Stats.StatChartConfig(
            log_file_path=path,
            y_axis_name="Server Boosters",
            color_tuple=(244, 127, 255)
        )
        url = Stats.render_stats_image(chart_config)
        return url
    return "Weird, please ping <@743230678795288637>"