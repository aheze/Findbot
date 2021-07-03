# bot.py
import os
import discord

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.reactions = True
intents.members = True
bot = commands.Bot(command_prefix='.', intents=intents)


# Emoji
# RED = "<:Red:860713765107400714>"
# GREEN = "<:Green:860713764742496258>"

with open('BadWords.txt', 'r') as f:
    global badwords  # You want to be able to access this throughout the code
    badwords = f.read().splitlines()

# get an emoji by name
async def get_emoji(name):
    emoji = None
    for guild in bot.guilds:
        print("emojis: ")
        print(guild.emojis)
        found_emoji = discord.utils.get(guild.emojis, name=name)

        if found_emoji:
            emoji = found_emoji
            break

    return emoji

@bot.command(name='react')
async def react(ctx, message_id, reaction):
    message = await ctx.fetch_message(message_id)
    emoji = await get_emoji(reaction)
    print(emoji)
    if emoji:
        await message.add_reaction(emoji)
    else:
        await ctx.message.reply(f"`{reaction}` emoji was not found")

@bot.command(name='clear_reacts')
async def set_reaction_roles(ctx, message_link):
    link = message_link.split('/')

    server_id = int(link[4])
    channel_id = int(link[5])
    message_id = int(link[6])

    server = bot.get_guild(server_id)
    channel = server.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    await message.clear_reactions()

@bot.event
async def on_message(message):
    msg = message.content.split()

    has_bad_word = False
    for word in badwords:
        if word in msg:

            print(f"Bad word: {word}, in {msg}")
            has_bad_word = True
            break
    
    if has_bad_word:
        channel = message.channel
        
        embed = discord.Embed(title="Don't say that >:(", description="Press <:Finder:859834757940903956>  ", color=0xFF5733)
        await message.delete()
        await channel.send(embed=embed)

    await bot.process_commands(message) # Needed to allow other commands to work


@bot.event
async def on_ready():
    print("Ready to test!")


bot.run(TOKEN)