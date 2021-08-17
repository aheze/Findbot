import Config
import FileContents
import ServerSettings
import Moderation

import regex as re
import discord
import unicodedata
import os

COLOR_GREEN = 0x08e800
COLOR_YELLOW = 0xffee00
COLOR_RED = 0xff0000

guild_to_word_map = {}
guild_to_regex_bad_words = {}


for server_folder in os.listdir('ServerSpecific'):
    guild_to_word_map[server_folder] = {}

    bad_words_file = FileContents.server_path(server_folder, "Config/BadWordsMap.txt")
    with open(bad_words_file, 'r') as f:
        badwords = f.read().splitlines()
        for word in badwords:
            word_split = word.split("/")
            checking_bad_word = word_split[0]
            alternatives = (word_split[1], word_split[2])
            guild_to_word_map[server_folder][checking_bad_word] = alternatives

    regex_bad_words_file = FileContents.server_path(server_folder, "Config/BadWordsRegex.txt")
    with open(regex_bad_words_file, 'r') as f:
        guild_to_regex_bad_words[server_folder] = f.read()

async def check_edit_censor(bot, payload):
    server = bot.get_guild(payload.guild_id)
    channel = server.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if message.author == bot.user:
        return
    else:
        await check_censor(bot, message, False)

async def check_censor(bot, message, send_replacement = True):
    if not ServerSettings.settings(message.guild.id)["swear_filter_enabled"]:
        return
    message_input = message.content

    author = message.author
    server = message.guild
    channel = message.channel
    member = server.get_member(author.id)
    member_roles = [role for role in member.roles if role.name == "Developer"]
    is_dev = len(member_roles) > 0

    (bad_words, replacement) = check_bad_words(str(message.guild.id), message_input, is_dev)

    if len(bad_words) > 0:

        embed = discord.Embed(description=replacement, color=COLOR_YELLOW)
        embed.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar.url)

        created_at = message.created_at
        edited_at = message.edited_at

        await message.delete()

        if send_replacement:
            if message.reference is not None:
                message_reference_id = message.reference.message_id
                original_message = await channel.fetch_message(message_reference_id)
                warning_message = await original_message.reply(embed=embed)
            else:
                warning_message = await channel.send(embed=embed)
                embed_description = message.content

                generic_bad_words = [x[0] for x in bad_words]
                original_bad_words = [x[1] for x in bad_words]
                cleaned_bad_words = list(set(original_bad_words))

                for original in cleaned_bad_words:
                    embed_description = re.sub(original, f"*__{original}__*", embed_description, flags=re.IGNORECASE)

                log_channel = Config.get_configurated_channel(bot=bot, guild_id=message.guild.id, channel_type="modlog")
                if not log_channel: 
                    print("No LOG CHANNEL")
                    await Moderation.warn_no_mod_channel(guild=server)
                    return

                if send_replacement:
                    embed_log = discord.Embed(title="Censored Message", color=0xfcba03)
                else:
                    embed_log = discord.Embed(title="Censored Edited Message", color=COLOR_RED)

                embed_log.set_author(name=message.author.display_name, url=f"https://discord.com/users/{message.author.id}", icon_url=message.author.avatar.url)
            
                if send_replacement:
                    embed_log.add_field(name="User details", value=f"{message.author.mention} ({message.author.id})", inline=False)
                    embed_log.add_field(name="Original message", value=embed_description, inline=False)
                    embed_log.add_field(name="Replaced message", value=replacement, inline=False)
                    embed_log.add_field(name="Original message ID", value=f"{message.id}", inline=True)
                    embed_log.add_field(name="Replaced message link", value=f"[{warning_message.id}]({warning_message.jump_url})", inline=True)
                else:
                    embed_log.add_field(name="User details", value=f"{message.author.mention} ({message.author.id})", inline=False)
                    embed_log.add_field(name="Updated message", value=embed_description, inline=False)
                    embed_log.add_field(name="Created time", value=created_at.strftime("%Y-%m-%d %l:%M:%S %p"), inline=True)
                    embed_log.add_field(name="Edited time", value=edited_at.strftime("%Y-%m-%d %l:%M:%S %p"), inline=True)
                    embed_log.add_field(name="Channel", value=channel.mention, inline=True)

                embed_log.set_footer(text=f"Censored words: {generic_bad_words}")
                await log_channel.send(embed=embed_log)

def check_bad_words(guild_id_str, input_str, is_dev):
    new_string = input_str

    # (filter name, user bad word)
    bad_words = []

    regex_bad_words = guild_to_regex_bad_words[guild_id_str]
    matches = list(re.finditer(regex_bad_words, remove_accents(input_str), re.IGNORECASE|re.UNICODE))
    for match in matches[::-1]:
        match_name = match.lastgroup[:-1]
        match_text = match.group(0)

        replacements = guild_to_word_map[guild_id_str].get(match_name, ("getfind.app", "getfind.app"))
        
        if is_dev:
            replacement = replacements[1]
        else:
            replacement = replacements[0]

        replacement_length = len(replacement)
        original_length = len(match_text)

        full_replacement = replacement
        if replacement_length < original_length:
            needed_count = original_length - replacement_length
            extra_characters = replacement[-1] * needed_count
            full_replacement += extra_characters

        full_replacement = f"*__{full_replacement}__*"
        new_string = new_string[:match.start()] + full_replacement + new_string[match.end():]
        bad_words.append((match_name, match_text))
        
    return (bad_words, new_string)

def remove_accents(s):
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))