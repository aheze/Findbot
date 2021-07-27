
import FileContents
import plotly.express as px
from plotly.graph_objs import *
import os

from datetime import datetime

DATE_FORMATTING = "%m.%d.%Y"

class StatChartConfig:
    def __init__(self, log_file_name, output_file_name, y_axis_name, color_tuple):
        self.log_file_name = log_file_name
        self.output_file_name = output_file_name
        self.y_axis_name = y_axis_name
        self.bar_color = f"rgba({color_tuple[0]}, {color_tuple[1]}, {color_tuple[2]}, 0.75)"
        self.border_color = f"rgb({color_tuple[0]}, {color_tuple[1]}, {color_tuple[2]})" 

def render_stats_image(chart_config: StatChartConfig):
    # if not os.path.exists("images"):
    #     os.mkdir("images")

    with open(f'z_ServerStats/{chart_config.log_file_name}.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        dates = []
        values = []

        for line in file_contents:
            line_split = line.split(":")
            date_string = line_split[0]
            value_string = line_split[1]

            date = datetime.strptime(date_string, DATE_FORMATTING)
            dates.append(date)
            value = int(value_string)
            values.append(value)

        data = {'dates': dates, 'y_vals': values}

        fig = px.bar(
            data,
            x='dates',
            y='y_vals',
            labels = {
                "dates": "Date",
                "y_vals": chart_config.y_axis_name
            }
        )

        fig.update_traces(
            marker_color=chart_config.bar_color,
            marker_line_color='rgba(0,0,0,0)',
            marker_line_width=1.5, opacity=0.6
        )

        layout = Layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="white",
            margin_l=0,
            margin_r=0,
            margin_t=0,
            margin_b=0,
        )    

        fig.update_xaxes(showline=True, linewidth=2, linecolor=chart_config.border_color, title_font_size=21)
        fig.update_yaxes(showline=True, linewidth=2, linecolor=chart_config.border_color, gridwidth=2, gridcolor='rgba(255,255,255, 0.3)', title_font_size=21)
        fig.update_layout(layout)

        output_url = f"z_ServerStats/{chart_config.output_file_name}.png"
        fig.write_image(output_url)
        return output_url


def update_or_append_file(keyword, string):
    line_overridden = False
    with open('z_ServerStats/ServerMembersLog.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
                
        for index, line in enumerate(file_contents):
            if keyword in line:
                file_contents[index] = string
                line_overridden = True
                break

    if line_overridden == False:
        file_contents.append(string)

    with open('z_ServerStats/ServerMembersLog.txt', 'w') as file:
        combined = FileContents.combine_file_contents(file_contents)
        file.write(combined)

def update_server_member_data(server):
    current_date = datetime.now()
    current_date_string = current_date.strftime(DATE_FORMATTING)
    current_member_count = server.member_count

    string = f"{current_date_string}:{current_member_count}\n"
    update_or_append_file(current_date_string, string)


GREEN = "<:Green:860713764742496258>"
async def update(ctx):
    print("up")
    update_server_member_data(ctx.guild)
    print("upasd")
    await ctx.message.add_reaction(GREEN)


