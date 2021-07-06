
import Utilities
import asyncio

async def react(bot, ctx, message_id, reaction):
    
    message = await ctx.fetch_message(message_id)
    emoji = Utilities.get_emoji(bot, reaction)
    if emoji:
        await message.add_reaction(emoji)
    else:
        await ctx.message.reply(f"`{reaction}` emoji was not found")

async def clear_reacts(bot, message_link):
    link = message_link.split('/')

    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])

    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    await message.clear_reactions()