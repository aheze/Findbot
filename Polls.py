import Utilities
import FileContents
import Stats
import discord

EMOJI_SERVER_ID = 869798779145027584
GREEN = "<:Green:860713764742496258>"

class PollInfo:
    def __init__(self, jump_url, title, choices, description, counts):
        self.jump_url = jump_url
        self.title = title
        self.choices = choices # ["Red", "Violet", "Cheese", "Other"]
        self.description = description
        self.counts = counts # [0, 4, 10, 3]

async def count_reactions(message):

    counts = []
    has_votes = False
    for reaction in message.reactions:
        if reaction.emoji.guild.id == 869798779145027584:
            count = reaction.count - 1
            counts.append(count)
            if not has_votes:
                has_votes = count > 0

    with open('Output/PollsLog.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
        for line in file_contents:
            if str(message.id) in line:

                line_split = line.split("<~meta~>", 2)
                title = line_split[1]
                choices_string = line_split[2]
                choices = choices_string.split("<~sep~>")

                max_count = max(counts)
                winning_indices = [i for i, j in enumerate(counts) if j == max_count]
                winning_choices = [f"**{choices[index]}**" for index in winning_indices]
                winning_text = Utilities.readable_list(winning_choices)

                if max_count == 1:
                    votes = "1 vote"
                else:
                    votes = f"{max_count} votes"

                if not has_votes:
                    description = "No one has voted yet!"
                elif len(winning_indices) > 1:
                    description = f"Poll result: {winning_text} (tied with {votes})"
                else:
                    description = f"Poll result: {winning_text} ({votes})"


                poll_info = PollInfo(
                    jump_url=message.jump_url,
                    title=title,
                    choices=choices,
                    description=description,
                    counts=counts
                )

                return poll_info


async def make_poll(bot, ctx, args):
    if args:
        message = " ".join(args)
        if message.startswith("show"):
            message_link = message.split("show")[1].strip()
            await show_poll_results(bot, message_link)
        else:
            message_split = message.split("?", 2)
            if len(message_split) > 2:
                title = message_split[0] + "?"
                choices = [choice.strip() for choice in message_split[2].split(",")]
            else:
                title = message_split[0]
                choices = [choice.strip() for choice in message_split[1].split(",")]
            

            color = read_poll_color(ctx.channel)
            hex_color = poll_color_to_hex(color)

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
                choices_string = "<~sep~>".join(choices)
                string = f"{sent_message.id}<~meta~>{title}<~meta~>{choices_string}\n"
                file.write(string)

            for emoji in emojis:
                await sent_message.add_reaction(emoji)

async def check_reply(bot, message):
    if message.reference is not None:
        if message.content == "show":
            original_message_reference_id = message.reference.message_id
            with open('Output/PollsLog.txt', 'r') as file:
                file_contents = FileContents.get_file_contents(file)
                for line in file_contents:
                    if str(original_message_reference_id) in line:
                        original_message = await message.channel.fetch_message(original_message_reference_id)
                        await send_poll_results(message.channel, original_message)

async def show_poll_results(bot, message_link):
    message = await Utilities.get_message_from_url(bot, message_link)
    await send_poll_results(message.channel, message)

async def send_poll_results(channel, message):

    color = read_poll_color(channel)   
    hex_color = poll_color_to_hex(color)
    poll_info = await count_reactions(message)

    chart_config = Stats.GenericChartConfig(
        output_file_name="PollOutput",
        color=color,
        counts=poll_info.counts,
        x_labels=poll_info.choices
    )

    image_url = Stats.render_chart(chart_config)
    embed = discord.Embed(title=poll_info.title, description=poll_info.description, color=hex_color)
    embed.set_author(name="Poll", url=poll_info.jump_url, icon_url="https://raw.githubusercontent.com/aheze/Findbot-Assets/main/Poll.png")
    url = 'attachment://image.png'
    file = discord.File(image_url, filename="image.png")
    embed.set_image(url=url)

    await channel.send(file=file, embed=embed)

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

def poll_color_to_hex(color):
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

    return hex_color