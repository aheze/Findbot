
import Utilities
import ReactionActions
import discord
import asyncio

role_id_to_color = {
    "Contributor": 0x00aeef,
    "Beta Tester": 0x00ad00,
    "Reviewer": 0xffc400,
    "Feedbacker": 0x8D70FF,
    "Birthday Boy": 0xff39d4,
    "Mod": 0x47FFA1
}

async def react(bot, ctx, message_id, reaction):
    
    message = await ctx.fetch_message(message_id)
    emoji = Utilities.get_emoji(bot, reaction)
    if emoji:
        await message.add_reaction(emoji)
    else:
        await ctx.message.reply(f"`{reaction}` emoji was not found")

async def clear_reacts(bot, message_link):
    message = await Utilities.get_message_from_url(bot, message_link)
    await message.clear_reactions()

async def set_claim_role(bot, ctx, user: discord.User, emoji_role_name: str, in_channel: discord.TextChannel, args):
    server = ctx.guild

    name_split = emoji_role_name.split("/")
    if len(name_split) > 1:
        emoji_name = name_split[0]
        role_name = name_split[1]
    else:
        emoji_name = name_split[0].replace(" ", "")
        role_name = name_split[0]

    emoji = Utilities.get_emoji(bot, emoji_name)
    role = discord.utils.get(server.roles, name=role_name)
    role_name = role.name

    color = role_id_to_color.get(role_name, 0x00aeef)
    embed = discord.Embed(title="Claim your role!", description=f"{user.mention}, thanks for being part of the Find server! You've been granted the **{role.mention}** role - press the reaction to claim it.", color=color)
    if args:
        reason = " ".join(args)
        embed.set_footer(text=f"Note from aheze: {reason}")

    message = await in_channel.send(embed=embed)
    channel = message.channel

    ReactionActions.save_reaction_action(server.id, channel.id, message.id, emoji.id, f"claim.{role.id}.{user.id}")
    await message.add_reaction(emoji)