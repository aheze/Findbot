import FileContents
import ServerSettings
import Utilities
import discord
GREEN = "<:Green:860713764742496258>"

async def configurate(ctx, name, channel):
    if channel:
        guild_id = str(ctx.guild.id)
        channel_id = str(channel.id)
        if name == "modlog":
            ServerSettings.write_settings(guild_id, "modlog", channel_id) 
        elif name == "status":
            ServerSettings.write_settings(guild_id, "status", channel_id)     

    await ctx.message.add_reaction(GREEN)

def get_configurated_channel(bot, guild_id, channel_type):
    log_server = bot.get_guild(guild_id)
    dict = ServerSettings.settings(guild_id)
    channel_id = dict[channel_type]
    if channel_id:
        log_channel = log_server.get_channel(int(channel_id))
        return log_channel
    else:
        return None
        


    # value = Utilities.read_value_from_file('Output/ServerConfig.txt', channel_type)
    # value_split = value.split("/")
    # server_id = int(value_split[0])
    # channel_id = int(value_split[1])
    # log_server = bot.get_guild(server_id)
    # log_channel = log_server.get_channel(channel_id)
    # return log_channel