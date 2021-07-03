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
bot = commands.Bot(command_prefix='!', intents=intents)

with open('BadWords.txt', 'r') as f:
    global badwords  # You want to be able to access this throughout the code
    badwords = f.read().splitlines()

# get an emoji by name
async def get_emoji(name):
    for guild in bot.guilds:
        print("emojis: ")
        print(guild.emojis)
        emoji = discord.utils.get(guild.emojis, name=name)

    if emoji:
        return emoji
    else:
        return None

@bot.command(name='react')
async def react(ctx, message_id, reaction):
    message = await ctx.fetch_message(message_id)
    emoji = await get_emoji(reaction)
    print(emoji)
    if emoji:
        await message.add_reaction(emoji)
    else:
        await ctx.message.reply(f"`{reaction}` emoji was not found")


@bot.event
async def on_message(message):
    msg = message.content

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