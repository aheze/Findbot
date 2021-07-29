import Utilities
import FileContents
import Stats
import discord

EMOJI_SERVER_ID = 869798779145027584
GREEN = "<:Green:860713764742496258>"

class PollInfo:
    def __init__(self, title, choices, counts):
        self.title = title
        self.choices = choices # ["Red", "Violet", "Cheese", "Other"]
        self.counts = counts # [0, 4, 10, 3]

async def count_reactions(message):
    print(message)

    counts = []
    for reaction in message.reactions:
        if reaction.emoji.guild.id == 869798779145027584:
            counts.append(reaction.count)

    with open('Output/PollsLog.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
        for line in file_contents:
            if str(message.id) in line:
                print("yep!")
                
                line_split = line.split(":", 1)
                print(line_split)
                title = line_split[0]
                choices_string = line_split[1]
                choices = choices_string.split("~~")

                poll_info = PollInfo(
                    title=title,
                    choices=choices,
                    counts=counts
                )

                print("return")

                return poll_info



async def make_poll(bot, ctx, args):
    if args:
        message = " ".join(args)
        if message.startswith("show"):
            message_id = message.split("show")[1].strip()
            await show_poll_results(bot, ctx, message_id)
        else:
            message_split = message.split("?", 2)
            if len(message_split) > 2:
                title = message_split[0] + "?"
                choices = [choice.strip() for choice in message_split[2].split(",")]
            else:
                title = message_split[0]
                choices = [choice.strip() for choice in message_split[1].split(",")]
            

            color = read_poll_color(ctx.channel)
            if color == "blue":
                hex_color = 0x00B2EA
            elif color == "green":
                hex_color = 0x3EDB0F
            elif color == "pink":
                hex_color = 0xFF45CA
            elif color == "purple":
                hex_color = 0xCD0CFE
            else:
                hex_color = 0xFCBB00

            poll_message_title = Utilities.random_message("poll")

            content = ""
            emojis = []
            for index, choice in enumerate(choices):
                emoji = get_choice_emoji(bot, color, index + 1)
                content += f"{emoji} {choice}\n"
                emojis.append(emoji)

            embed = discord.Embed(title=title, description=content, color=hex_color)
            embed.set_author(name=poll_message_title, icon_url="https://raw.githubusercontent.com/aheze/Findbot-Assets/main/Poll.png")
            sent_message = await ctx.send(embed=embed)

            with open('Output/PollsLog.txt', 'a') as file:
                choices_string = "~~".join(choices)
                string = f"{sent_message.id}:{choices_string}"
                file.write(string)

            for emoji in emojis:
                await sent_message.add_reaction(emoji)


async def show_poll_results(bot, ctx, message_id):
    color = read_poll_color(ctx.channel)   
    message = await ctx.channel.fetch_message(message_id)

    poll_info = await count_reactions(message)

    print("Ok.")

    chart_config = Stats.GenericChartConfig(
        output_file_name="PollOutput",
        color=color,
        counts=poll_info.counts,
        x_labels=poll_info.choices
    )

    image_url = Stats.render_chart(chart_config)
    embed = discord.Embed(description=f"Output")
    url = 'attachment://image.png'
    file = discord.File(image_url, filename="image.png")
    embed.set_image(url=url)

    await ctx.send(file=file, embed=embed)

def get_choice_emoji(bot, color, index):
    letter = chr(ord('@') + index)
    emoji_name = f"{letter}_{color}"
    emoji = Utilities.get_emoji(bot, emoji_name)
    return emoji


def read_poll_color(channel):
    with open("Output/ServerConfig.txt", 'r') as file:
        file_contents = FileContents.get_file_contents(file)
        for line in file_contents:
            if f'pollcolor-{channel.id}' in line:
                color = line.split(":")[1].strip()
                return color

async def set_poll_color(ctx, color):
    channel_id = str(ctx.channel.id)
    string = f'pollcolor-{channel_id}:{color}\n'

    with open("Output/ServerConfig.txt", 'r') as file:
        file_contents = FileContents.get_file_contents(file)
        new_file_contents = file_contents

        matching_user_index = index_containing_substring(file_contents, f'pollcolor-{channel_id}')
        if matching_user_index == -1:
            new_file_contents.append(string)
        else:
            new_file_contents[matching_user_index] = string

    with open("Output/ServerConfig.txt", 'w') as file:
        combined = FileContents.combine_file_contents(new_file_contents)
        file.write(combined)

    await ctx.message.add_reaction(GREEN)

def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1