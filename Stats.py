import Utilities
import FileContents
import plotly.express as px
from plotly.graph_objs import *
import os

from datetime import datetime
DATE_FORMATTING = "%m.%d.%Y"

class StatChartConfig:
    def __init__(self, log_file_path, output_file_name, y_axis_name, color_tuple):
        self.log_file_path = log_file_path
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
    x_vals = list(range(1, len(chart_config.counts) + 1))
    data = {'choices': x_vals, 'y_vals': chart_config.counts}

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

    fig.update_coloraxes(showscale=False)
    fig.update_traces(
        showlegend=False,
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
        xaxis = dict(
            type='category',
            tickmode = 'array',
            tickvals = x_vals,
            ticktext = chart_config.x_labels
        ),
        yaxis = dict(
            tickmode = 'linear',
            tick0 = 1,
            dtick = 0
        ),
        
    )   

    fig.update_xaxes(automargin=True, showline=True, linewidth=2, linecolor='rgb(96, 181, 255)', tickfont_size=24)
    fig.update_yaxes(rangemode="tozero", showline=True, linewidth=2, linecolor='rgb(96, 181, 255)', gridwidth=2, gridcolor='rgba(255,255,255, 0.3)', tickfont_size=24)
    fig.update_layout(layout)

    output_url = f"Output/Images/{chart_config.output_file_name}.png"
    fig.write_image(output_url)

    return output_url


def render_stats_image(chart_config: StatChartConfig):
    with open(chart_config.log_file_path, 'r') as file:
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

def update_server_member_data(server):
    current_date = datetime.now()
    current_date_string = current_date.strftime(DATE_FORMATTING)
    current_member_count = str(server.member_count)
    
    Utilities.save_key_value_to_file('Output/Logs/ServerMembersLog.txt', current_date_string, current_member_count)


GREEN = "<:Green:860713764742496258>"
async def update(ctx):
    update_server_member_data(ctx.guild)
    await ctx.message.add_reaction(GREEN)


