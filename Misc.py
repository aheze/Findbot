import discord
import codecs
from cairosvg import svg2png
import asyncio

async def ping(ctx):
    await ctx.message.reply("pong")

async def get_pfp(ctx, user: discord.User):
    user_pfp_link = user.avatar_url
    embed = discord.Embed(description=f"{user.name}'s profile pic:", color=0x008fd6)
    embed.set_image(url=user_pfp_link)
    await ctx.send(embed=embed)

async def get_color(ctx, color: str):
    color_string = color
    with codecs.open('y_FindMark.svg', encoding='utf-8', errors='ignore') as f:
        print("opening")
        content = f.read()
        print(content)
        old_colour = 'FFFFFF'
        new_colour = color_string
        new_SVG = content.replace(old_colour, new_colour)

        hex_str = f"0x{color}"
        hex_int = int(hex_str, 16)
        new_int = hex_int + 0x200


        print("new int")
        svg2png(bytestring=new_SVG,write_to='coloroutput.png', scale=0.2)
        embed = discord.Embed(description=f"Color", color=new_int)

        print("URL")
        url = 'attachment://coloroutput.png'
        file = discord.File("coloroutput.png", filename="coloroutput.png")
        embed.set_image(url=url)

        print("set")
        await ctx.send(file=file, embed=embed)
        print("setn!!")