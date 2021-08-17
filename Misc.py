import discord
import codecs
from cairosvg import svg2png

async def send(channel: discord.TextChannel, args):
    if args:
        message = " ".join(args)
        await channel.send(message)

async def dance(ctx):
    url = "https://raw.githubusercontent.com/aheze/Findbot-Assets/main/UsagiDance.gif"
    embed = discord.Embed(description=f"Here is a dance", color=0xa200ad)
    embed.set_image(url=url)
    await ctx.send(embed=embed)
    
async def ping(bot, ctx):
    embed = discord.Embed(description=f"Thanks to <@788274635871092777>.", color=0x6060ec)
    await ctx.message.reply(f"Pong! My latency is ~{round(bot.latency * 1000)}ms.", embed=embed)

async def get_pfp(ctx, user: discord.User):
    user_pfp_link = user.avatar.url
    embed = discord.Embed(description=f"{user.name}'s profile pic:", color=0x008fd6)
    embed.set_image(url=user_pfp_link)
    await ctx.send(embed=embed)

async def get_color(ctx, color: str):
    color_string = color
    if color_string.lower() == 'ffffff':
        color_string = 'FFF'

    with codecs.open('Assets/FindMark.svg', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        old_colour = 'FFFFFF'
        new_colour = color_string
        new_SVG = content.replace(old_colour, new_colour)
        
        hex_str = f"0x{color_string}"
        hex_int = int(hex_str, 16)
        new_int = hex_int + 0x200

        svg2png(bytestring=new_SVG,write_to='coloroutput.png', scale=0.2)
        embed = discord.Embed(description=f"Color", color=new_int)

        url = 'attachment://coloroutput.png'
        file = discord.File("coloroutput.png", filename="coloroutput.png")
        embed.set_image(url=url)

        await ctx.send(file=file, embed=embed)