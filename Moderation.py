import ReactionActions
import FileContents
import TimedActions
import Utilities
import discord

from datetime import datetime, timedelta
import asyncio

GREEN = "<:Green:860713764742496258>"
GREEN_ID = "860713764742496258"
MUTED_ID = 861271876185751553

with open('BadWords.txt', 'r') as f:
    global badwords  # You want to be able to access this throughout the code
    badwords = f.read().splitlines()

async def set_modlog(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    channel_id = str(channel.id)
    string = f'modlog:{guild_id}:{channel_id}\n'

    line_overridden = False
    with open('z_ServerConfig.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
                
        for index, line in enumerate(file_contents):
            if "modlog:" in line:
                file_contents[index] = string
                line_overridden = True
                break

    if line_overridden == False:
        with open('z_ServerConfig.txt', 'a') as file:
            file.write(string)
    else:
        with open('z_ServerConfig.txt', 'w') as file:
            combined = FileContents.combine_file_contents(file_contents)
            file.write(combined)

    await ctx.message.add_reaction(GREEN)

async def unmute(bot, ctx, user: discord.User, reason = ""):
    print("unmute!")
    server = ctx.guild
    member = server.get_member(user.id)
    muted_role = discord.utils.get(server.roles, id=MUTED_ID)
    await member.remove_roles(muted_role)

    keywords = ["unmute", str(user.id)]
    TimedActions.remove_timed_actions(keywords)
    embed = discord.Embed(description=f"Unmuted {member.mention}", color=0x1ce800)
    await ctx.send(embed=embed)

    log_channel = Utilities.get_modlog_channel(bot)
    embed_log = discord.Embed(title="Unmuted", color=0x1ce800)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    embed_log.add_field(name="Unmuter:", value=f"{ctx.author.mention} ({ctx.author.id})", inline=True)
    embed_log.add_field(name="Unmuted:", value=f"{member.mention} ({member.id})", inline=True)

    await log_channel.send(embed=embed_log)

async def mute(bot, ctx, user: discord.User, args):
    print("mute!")

    if args:
        first_arg = args[0]
        if first_arg[0].isalpha():
            time = "3"
            reason = " ".join(args)
        else:
            time = first_arg
            reason = " ".join(args[1:])
    else:
        time = "3"
        reason = ""

    delay_time = datetime.now()
    allowed_extensions = ("s", "m", "h", "d")
    if time.endswith(allowed_extensions):

        time_int = int(time[:-1])
        last_character = time[-1]
        if last_character == "s":
            delay_time += timedelta(seconds=time_int)
            length_string = f"{time_int} seconds"
        elif last_character == "m":
            delay_time += timedelta(minutes=time_int)
            length_string = f"{time_int} minutes"
        elif last_character == "h":
            delay_time += timedelta(hours=time_int)
            length_string = f"{time_int} hours"
        else:
            delay_time += timedelta(days=time_int)
            length_string = f"{time_int} days"
            
    elif time[-1].isalpha():
        time_int = int(time[:-1])
        delay_time += timedelta(seconds=time_int)
        length_string = f"{time_int} seconds"
    else: # just int, so seconds
        time_int = int(time)
        delay_time += timedelta(minutes=time_int)
        length_string = f"{time_int} minutes"
    
    server = ctx.guild
    member = server.get_member(user.id)
    muted_role = discord.utils.get(server.roles, id=MUTED_ID)
    action_string = f"unmute.{ctx.guild.id}.{user.id}"
    await member.add_roles(muted_role)

    print("action:")
    print(action_string)

    keywords = ["unmute", str(user.id)]
    TimedActions.remove_timed_actions(keywords)
    TimedActions.remove_timed_actions(action_string)
    TimedActions.save_timed_action(delay_time, action_string)

    embed = discord.Embed(description=f"Muted {member.mention} for {length_string}", color=0xe8fc03)
    
    if reason:
        reason_string = f"Reason: {reason}"
    else:
        reason_string = "No reason given"
    embed.set_footer(text=reason_string)

    await ctx.send(embed=embed)

    print("sent!")

    log_channel = Utilities.get_modlog_channel(bot)
    print("log")
    embed_log = discord.Embed(title=f"Muted for {length_string}", color=0xe8fc03)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    embed_log.add_field(name="Muter:", value=f"{ctx.author.mention} ({ctx.author.id})", inline=True)
    embed_log.add_field(name="Muted:", value=f"{member.mention} ({member.id})", inline=True)
    embed_log.set_footer(text=reason_string)

    print("done config")
    await log_channel.send(embed=embed_log)
    print("send")

async def check_censor(bot, message):
    print("cehck!")
    msg = message.content.split()

    bad_word = ""
    for word in badwords:
        if word.lower() in msg:
            print(f"Bad word: {word}, in {msg}")
            bad_word = word
            break
    
    if bad_word != "":
        channel = message.channel

        embed = discord.Embed(description=f"{message.author.mention}, don't say that >:(", color=0xFF0000)
        embed.set_footer(text=f"React with the check to dismiss")

        await message.delete()
        warning_message = await channel.send(embed=embed)
        warning_channel = warning_message.channel
        warning_server = warning_channel.guild

        ReactionActions.save_reaction_action(warning_server.id, warning_channel.id, warning_message.id, GREEN_ID, "delete")
        await warning_message.add_reaction(GREEN)

        with open('z_ServerConfig.txt', 'r') as file:
            file_contents = FileContents.get_file_contents(file)

            for line in file_contents:
                if "modlog:" in line:
                    line_split = line.split(":")
                    server_id = int(line_split[1])
                    channel_id = int(line_split[2])

                    log_server = bot.get_guild(server_id)
                    log_channel = log_server.get_channel(channel_id)

                    embed_log = discord.Embed(title="Censored Message:", description=f"{message.content}", color=0xFF0000)
                    embed_log.set_author(name=message.author.display_name, url=f"https://discord.com/users/{message.author.id}", icon_url=message.author.avatar_url)
                    embed_log.add_field(name="User details", value=f"{message.author.mention} ({message.author.id})", inline=False)
                    embed_log.set_footer(text=f"Censored word: {bad_word}")
                    await log_channel.send(embed=embed_log)
                    break