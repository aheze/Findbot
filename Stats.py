
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

class GenericChartConfig:
    def __init__(self, output_file_name, color, counts, x_labels):
        self.output_file_name = output_file_name
        self.counts = counts
        self.x_labels = x_labels

        if color == "blue":
            self.start_color = '#00AEEF'
            self.end_color = '#00EF90'
        elif color == "green":
            self.start_color = '#42E100'
            self.end_color = '#0082EF'
        elif color == "pink":
            self.start_color = '#FF3CD0'
            self.end_color = '#FFD163'
        elif color == "purple":
            self.start_color = '#D900FF'
            self.end_color = '#00EFEC'
        else:
            self.start_color = '#FFB700'
            self.end_color = '#C7FF00'
        
        

def render_chart(chart_config: GenericChartConfig):
    # START_COLOR_BLUE = '#00AEEF'
    # START_COLOR_GREEN = '#42E100'
    # START_COLOR_PINK = '#FF3CD0'
    # START_COLOR_PURPLE = '#D900FF'
    # START_COLOR_YELLOW = '#FFB700'

    # END_COLOR_BLUE = '#00EF90'
    # END_COLOR_GREEN = '#0082EF'
    # END_COLOR_PINK = '#FFD163'
    # END_COLOR_PURPLE = '#00EFEC'
    # END_COLOR_YELLOW = '#C7FF00'

    print("render")

    # data = {
    #     1: 10,
    #     2: 7,
    #     3: 12,
    #     4: 1
    # }

    # x_vals = list(data.keys())
    # y_vals = list(data.values())

    print("x")
    x_vals = list(range(1, len(chart_config.counts) + 1))
    data = {'choices': x_vals, 'y_vals': chart_config.counts}

    print("X DONE")

    print(x_vals)
    print(chart_config.counts)

    print(chart_config.start_color)
    print(chart_config.end_color)

    fig = px.bar(
        data,
        x='choices',
        y='y_vals',
        labels = {
            "choices": "",
            "y_vals": ""
        },
        color="choices",
        color_continuous_scale=[chart_config.start_color, chart_config.end_color]
    )

    print("BAR DONe")
    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        showlegend=False,
        marker_line_color='rgba(0,0,0,0)',
        marker_line_width=1.5, opacity=0.6
        
    )

    print("lay")

    layout = Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        margin_l=0,
        margin_r=0,
        margin_t=0,
        margin_b=0,
        xaxis = dict(
            tickmode = 'array',
            tickvals = x_vals,
            ticktext = chart_config.x_labels
        )
    )   

    print("Donelay")

    fig.update_xaxes(showline=True, linewidth=2, linecolor='rgb(96, 181, 255)', title_font_size=21)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='rgb(96, 181, 255)', gridwidth=2, gridcolor='rgba(255,255,255, 0.3)', title_font_size=21)
    fig.update_layout(layout)

    output_url = f"Output/Images/{chart_config.output_file_name}.png"
    fig.write_image(output_url)

    print("Done!")
    return output_url


def render_stats_image(chart_config: StatChartConfig):
    with open(f'Output/Images/{chart_config.log_file_name}.txt', 'r') as file:
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

        output_url = f"Output/Images/{chart_config.output_file_name}.png"
        fig.write_image(output_url)
        return output_url


def update_or_append_file(keyword, string):
    line_overridden = False
    with open('Output/Logs/ServerMembersLog.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
                
        for index, line in enumerate(file_contents):
            if keyword in line:
                file_contents[index] = string
                line_overridden = True
                break

    if line_overridden == False:
        file_contents.append(string)

    with open('Output/Logs/ServerMembersLog.txt', 'w') as file:
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
    update_server_member_data(ctx.guild)
    await ctx.message.add_reaction(GREEN)


