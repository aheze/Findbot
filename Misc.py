import discord
import asyncio

async def ping(ctx):
    print("Ping in misc!")
    await ctx.message.reply("pong")

async def get_pfp(ctx, user: discord.User):
    print("PFPPPP")
    user_pfp_link = user.avatar_url
    embed = discord.Embed(description=f"{user.name}'s profile pic:", color=0xe8ba00)
    embed.set_image(url=user_pfp_link)
    await ctx.send(embed=embed)