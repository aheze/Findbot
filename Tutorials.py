
import FileContents
import Utilities
import discord

step_colors = [
    "009BD5",
    "0081D5",
    "0050D5",
    "000AD5",
    "4100D5",
    "7E00D5",
    "B000D5",
    "D500AB",
    "D50068"
]

GREEN = "<:Green:860713764742496258>"
PROGRESS_EMOJI_ID = 863079541675917402


async def send_tutorial(bot, ctx, tutorial_name):
    tutorials = []
    with open('y_Tutorials.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)

        # 0: rate
        # 1: How to rate the app
        # 2: First, open...
        # 3: Then......
        current_tutorial = []
        for line in file_contents:
            tutorial_line = line
            if line.startswith("(T:"):
                current_tutorial = []
                tutorials.append(current_tutorial)
                
                line_split = line.split(")", 1)
                command_line = line_split[0]
                command = command_line.split(":", 1)[1].strip()
                current_tutorial.append(command)

                tutorial_line = line_split[1].strip()
            current_tutorial.append(tutorial_line)
        
    for tutorial in tutorials:
        if tutorial[0] == tutorial_name.lower():
            message_ids = []

            channel = ctx.channel

            title = tutorial[1]
            title_message = await channel.send(f"**{title}**")
            channel = title_message.channel
            server = title_message.guild
            title_message_string = f"{server.id}/{channel.id}/{title_message.id}"
            message_ids.append(title_message_string)

            for i in range(2, len(tutorial)):
                step_number = i - 1

                image_url = ""
                raw_line = tutorial[i]
                split_line = raw_line.split("<img>")
                if len(split_line) > 1:
                    line = split_line[0]
                    image_url = split_line[1]
                else:
                    line = raw_line

                line = line.replace("<n>", "\n")
                
                hex_str = f"0x{step_colors[i - 2]}"
                hex_int = int(hex_str, 16)
                new_int = hex_int + 0x200

                embed = discord.Embed(description=line, color=new_int)
                embed.set_author(name=f"Step {step_number}", icon_url=f"https://raw.githubusercontent.com/aheze/Findbot-Assets/main/Step{step_number}.png")
                if image_url:
                    url = 'attachment://image.png'
                    file = discord.File(image_url, filename="image.png")
                    embed.set_image(url=url)
                    message = await channel.send(file=file, embed=embed)

                    channel = message.channel
                    server = message.guild
                    message_string = f"{server.id}/{channel.id}/{message.id}"
                    message_ids.append(message_string)
                else:
                    message = await channel.send(embed=embed)

                    channel = message.channel
                    server = message.guild
                    message_string = f"{server.id}/{channel.id}/{message.id}"
                    message_ids.append(message_string)

            messages_joined = ",".join(message_ids)
            with open('z_TutorialsLog.txt', 'a') as file:
                string=f"{tutorial[0]}:{messages_joined}\n"
                file.write(string)

            break

async def unsend_latest_tutorial(bot, ctx, specific_command_name):
    progress_reaction = Utilities.get_emoji_from_id(bot, PROGRESS_EMOJI_ID)
    await ctx.message.add_reaction(progress_reaction)
    latest_line = ""
    new_file_contents = []
    with open('z_TutorialsLog.txt', 'r') as file:
        file_contents = list(FileContents.get_file_contents(file))

        if specific_command_name:
            reversed_contents = file_contents
            reversed_contents.reverse()

            for line in file_contents:
                if specific_command_name.lower() in line:
                    latest_line = line
                    reversed_contents.remove(line)
                    reversed_contents.reverse()
                    new_file_contents = reversed_contents
                    break
        else:
            latest_line = file_contents[-1]
            new_file_contents = file_contents[:-1]

    components = latest_line.strip().split(":")  # 0 is time, 1 is action
    messages_string = components[1]
    message_links = messages_string.split(",")

    for message_link in message_links:
        message_split = message_link.split("/")
        server_id = int(message_split[0])
        channel_id = int(message_split[1])
        message_id = int(message_split[2])

        server = bot.get_guild(server_id)
        channel = server.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.delete()

    await ctx.message.add_reaction(GREEN)
    await ctx.message.remove_reaction(progress_reaction, bot.user)

    with open('z_TutorialsLog.txt', 'w') as file:
        combined = FileContents.combine_file_contents(new_file_contents)
        file.write(combined)

        