
import Utilities
import ReactionActions
import discord
import asyncio

role_id_to_color = {
    859674348008243211: 0x00aeef, # Contributor
    859674301770629130: 0x00ad00, # Beta Tester
    859674262561882133: 0xffc400, # Reviewer
    859676010529816587: 0xd757ff # Feedbacker
}

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

async def set_claim_role(bot, ctx, user: discord.User, emoji_name: str, role_name: str, in_channel: discord.TextChannel, args):
    server = ctx.guild

    emoji = Utilities.get_emoji(bot, emoji_name)
    role = discord.utils.get(server.roles, name=role_name)

    role_id = int(role.id)
    embed = discord.Embed(title="Claim your role!", description=f"{user.mention}, thanks for being part of the Find server! You've been granted the {role.mention} role - press the reaction to claim it.", color=role_id_to_color[role_id])
    if args:
        reason = " ".join(args)
        embed.set_footer(text=f"Note from aheze: {reason}")

    message = await in_channel.send(embed=embed)
    channel = message.channel
    
    ReactionActions.save_reaction_action(server.id, channel.id, message.id, emoji.id, f"claim.{role.id}.{user.id}")
    await message.add_reaction(emoji)