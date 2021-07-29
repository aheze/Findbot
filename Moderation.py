
import ModerationStorage
import FileContents
import TimedActions
import Utilities
import discord

from datetime import datetime, timedelta

COLOR_GREEN = 0x08e800
COLOR_YELLOW = 0xffee00
COLOR_RED = 0xff0000

GREEN = "<:Green:860713764742496258>"
GREEN_ID = "860713764742496258"
TRASH = "<:Trash:864378434980282369>"
TRASH_ID = 864378434980282369
MUTED_ID = 861271876185751553
MEMBER_ROLE_ID = 862919875060039680


async def give_all_member(ctx):
    server = ctx.guild
    member_role = discord.utils.get(server.roles, id=MEMBER_ROLE_ID)
    muted_role = discord.utils.get(server.roles, id=MUTED_ID)

    for member in server.members:
        if muted_role not in member.roles:
            await member.add_roles(member_role)
            
    await ctx.message.add_reaction(GREEN)


async def give_member_role(member):
    server = member.guild
    member_role = discord.utils.get(server.roles, id=MEMBER_ROLE_ID)
    await member.add_roles(member_role)

async def set_modlog(ctx, channel: discord.TextChannel):
    guild_id = str(ctx.guild.id)
    channel_id = str(channel.id)
    string = f'modlog:{guild_id}:{channel_id}\n'

    line_overridden = False
    with open('Output/ServerConfig.txt', 'r') as file:
        file_contents = FileContents.get_file_contents(file)
                
        for index, line in enumerate(file_contents):
            if "modlog:" in line:
                file_contents[index] = string
                line_overridden = True
                break

    if line_overridden == False:
        with open('Output/ServerConfig.txt', 'a') as file:
            file.write(string)
    else:
        with open('Output/ServerConfig.txt', 'w') as file:
            combined = FileContents.combine_file_contents(file_contents)
            file.write(combined)

    await ctx.message.add_reaction(GREEN)

async def ban(bot, ctx, user: discord.User, args):
    print("ban")
    server = ctx.guild

    if args:
        reason = " ".join(args)
        reason_string = f"Reason: {reason}"
    else:
        reason_string = "No reason given"

    member = server.get_member(user.id)
    log_channel = Utilities.get_modlog_channel(bot)
    embed_log = discord.Embed(title=f"Banned", color=COLOR_RED)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    embed_log.add_field(name="Banner:", value=f"{ctx.author.mention} ({ctx.author.id})", inline=True)
    embed_log.add_field(name="Banned:", value=f"{member.mention} ({member.id})", inline=True)
    embed_log.set_footer(text=reason_string)

    await server.ban(user, delete_message_days=0)
    await log_channel.send(embed=embed_log)
    await ctx.message.add_reaction(GREEN)

async def unban(bot, ctx, user: discord.User, args):
    server = ctx.guild

    if args:
        reason = " ".join(args)
        reason_string = f"Reason: {reason}"
    else:
        reason_string = "No reason given"

    log_channel = Utilities.get_modlog_channel(bot)
    embed_log = discord.Embed(title=f"Unbanned", color=COLOR_GREEN)
    embed_log.set_author(name=user.display_name, url=f"https://discord.com/users/{user.id}", icon_url=user.avatar_url)
    embed_log.add_field(name="Unbanner:", value=f"{ctx.author.mention} ({ctx.author.id})", inline=True)
    embed_log.add_field(name="Unbanned:", value=f"{user.mention} ({user.id})", inline=True)
    embed_log.set_footer(text=reason_string)

    await server.unban(user)
    await log_channel.send(embed=embed_log)
    await ctx.message.add_reaction(GREEN)

async def unmute(bot, ctx, user: discord.User, args):
    await general_unmute(bot, ctx.guild, ctx.channel, ctx.author, user, args)

async def general_unmute(bot, server, channel, unmuter, muted_user, args):
    member = server.get_member(muted_user.id)
    muted_role = discord.utils.get(server.roles, id=MUTED_ID)
    await member.remove_roles(muted_role)

    if args:
        reason = " ".join(args)
        reason_string = f"Reason: {reason}"
    else:
        reason_string = "No reason given"

    keywords = ["unmute", str(muted_user.id)]
    TimedActions.remove_timed_actions(keywords)
    if channel:
        embed = discord.Embed(description=f"Unmuted {member.mention}", color=COLOR_GREEN)
        embed.set_footer(text=reason_string)
        await channel.send(embed=embed)

    log_channel = Utilities.get_modlog_channel(bot)
    embed_log = discord.Embed(title="Unmuted", color=COLOR_GREEN)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    embed_log.add_field(name="Unmuter:", value=f"{unmuter.mention} ({unmuter.id})", inline=True)
    embed_log.add_field(name="Unmuted:", value=f"{member.mention} ({member.id})", inline=True)
    embed_log.set_footer(text=reason_string)

    await log_channel.send(embed=embed_log)

    role_ids = ModerationStorage.get_roles_from_storage(muted_user.id)
    for role_id in role_ids:
        role = discord.utils.get(server.roles, id=int(role_id))
        await member.add_roles(role)

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
    
    member_roles = [role for role in member.roles if role.name != "@everyone"]
    user_roles = [str(role.id) for role in member_roles]
    joined = ",".join(user_roles)
    ModerationStorage.save_roles_to_storage(user.id, joined)

    await member.add_roles(muted_role)
    for role in member_roles:
        await member.remove_roles(role)
    

    action_string = f"unmute.{ctx.guild.id}.{user.id}"
    keywords = ["unmute", str(user.id)]
    TimedActions.remove_timed_actions(keywords)
    TimedActions.remove_timed_actions(action_string)
    TimedActions.save_timed_action(delay_time, action_string)

    embed = discord.Embed(description=f"Muted {member.mention} for {length_string}", color=COLOR_YELLOW)
    
    if reason:
        reason_string = f"Reason: {reason}"
    else:
        reason_string = "No reason given"
    embed.set_footer(text=reason_string)

    await ctx.send(embed=embed)

    log_channel = Utilities.get_modlog_channel(bot)
    embed_log = discord.Embed(title=f"Muted for {length_string}", color=COLOR_YELLOW)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar_url)
    embed_log.add_field(name="Muter:", value=f"{ctx.author.mention} ({ctx.author.id})", inline=True)
    embed_log.add_field(name="Muted:", value=f"{member.mention} ({member.id})", inline=True)
    embed_log.set_footer(text=reason_string)

    await log_channel.send(embed=embed_log)

