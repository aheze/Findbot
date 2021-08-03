
import FileContents
import Utilities
import discord


EVENT_NAME = "Funcing destroy the bot"
EVENT_DESCRIPTION = "Exploit <@784531493204262942>'s censoring loopholes: **get 1 point** for every should-be-censored word or false positive! Spam test words in <#864710025460187156>. Challenge ends July 15th, 11:59 PM PST."
EVENT_FOOTER = 'Be at the top to get the "Beta Tester" role!'

async def event_leaderboard(bot, ctx, ping = None):
    with open("Output/Events.txt", 'r') as file:

        leaderboard = []
        file_contents = FileContents.get_file_contents(file)
        for line in file_contents:
            line_split = line.split(":")
            user_id = int(line_split[0])
            user = bot.get_user(user_id)
            number = int(line_split[1])

            tuple = (user, number)
            leaderboard.append(tuple)

        leaderboard.sort(key=lambda tup: tup[1], reverse=True)  # sorts in place

        leaderboard_description = ""
        for (index, tuple) in enumerate(leaderboard):
            user = tuple[0]
            points = tuple[1]

            starting_trophy = ""
            if index == 0:
                starting_trophy = Utilities.get_emoji(bot, "First")
            elif index == 1:
                starting_trophy = Utilities.get_emoji(bot, "Second")
            elif index == 2:
                starting_trophy = Utilities.get_emoji(bot, "Third")
            else:
                starting_trophy = Utilities.get_emoji(bot, "NotSelected")

            new_line = ""
            if points == 1:
                new_line += f"{starting_trophy} {points} point: "
            else:
                new_line += f"{starting_trophy} {points} points: "

            if ping:
                new_line += f"{user.mention}\n"
            else:
                new_line += f"**{user.name}**\n"

            leaderboard_description += new_line

        description_start = EVENT_DESCRIPTION
        description = f"{description_start}\n\n{leaderboard_description}"

        channel = ctx.channel
        embed = discord.Embed(title=f'Leaderboard for the "{EVENT_NAME}" event!', description=description, color=0xebc334)
        embed.set_footer(text=EVENT_FOOTER)

        await channel.send(embed=embed)