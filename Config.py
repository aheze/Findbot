import FileContents
import Utilities
import discord
GREEN = "<:Green:860713764742496258>"

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

async def configurate(ctx, name, channel):
    if channel:
        if name == "modlog":
            guild_id = str(ctx.guild.id)
            channel_id = str(channel.id)
            key = "modlog"
            value = f"{guild_id}/{channel_id}" 
            Utilities.save_key_value_to_file('Output/ServerConfig.txt', key, value)     
        elif name == "status":
            guild_id = str(ctx.guild.id)
            channel_id = str(channel.id)
            key = "status"
            value = f"{guild_id}/{channel_id}" 
            Utilities.save_key_value_to_file('Output/ServerConfig.txt', key, value)     

    await ctx.message.add_reaction(GREEN)

def get_configurated_channel(bot, channel_type):
    value = Utilities.read_value_from_file('Output/ServerConfig.txt', channel_type)
    value_split = value.split("/")
    server_id = int(value_split[0])
    channel_id = int(value_split[1])
    log_server = bot.get_guild(server_id)
    log_channel = log_server.get_channel(channel_id)
    return log_channel