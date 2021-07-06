
import Utilities
import ReactionActions

import discord
import asyncio

RED = "<:Red:860713765107400714>"
GREEN = "<:Green:860713764742496258>"

async def set_reaction_roles(bot, ctx, message_link, reaction_roles):

    print("set reaction roles!")
    link = message_link.split('/')
    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])
    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)

    print("channel:")
    print(channel)
    message = await channel.fetch_message(message_id)
    print("message")
    emoji_not_founds = []
    role_not_founds = []
    duplicate_roles_messages = []

    # message address : emoji ID : action (assign role)
    for reaction_role in reaction_roles:
        print("Lllop")
        print("rea: ")
        print(reaction_role)
        emoji_to_role = reaction_role.split(":")
        print("emoooo:")
        print(emoji_to_role)
        print(reaction_role.split(":"))
        print("emo to row:")
        emoji = Utilities.get_emoji(bot, emoji_to_role[0])
        print(emoji)
        print("emo about")
        if emoji:
            print("yes emo")
            role = discord.utils.get(server.roles, name=emoji_to_role[1])
            print("role")
            print(role)
            if role:
                role_id = role.id
                has_error = ReactionActions.save_reaction_action(server_id, channel_id, message_id, emoji.id, f"role.{role_id}", "z_PermanentReactionActions.txt")
                if has_error:
                    message = f"`{emoji.name}` emoji is already assigned to `{role.name}` role"
                    duplicate_roles_messages.append(message)
                else:
                    await message.add_reaction(emoji)
            else:
                role_not_founds.append(emoji_to_role[1])
        else:
            print("NO emo")
            emoji_not_founds.append(emoji_to_role[0])

    if not emoji_not_founds and not role_not_founds and not duplicate_roles_messages:
        await ctx.message.add_reaction(GREEN)
    else:
        await ctx.message.add_reaction(RED)

    if emoji_not_founds:
        error_message = ""
        for emoji in emoji_not_founds:
            error = f"Emoji not found: {emoji}\n"
            error_message += error
        await ctx.message.reply(error_message)


    if role_not_founds:
        error_message = ""
        for role in role_not_founds:
            error = f"Role not found: {role}\n"
            error_message += error
        await ctx.message.reply(error_message)

    if duplicate_roles_messages:
        duplicate_roles_message = "\n".join(duplicate_roles_messages)
        await ctx.message.reply(duplicate_roles_message)