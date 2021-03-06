import Stats
import Moderation
import Config
from humanfriendly import format_timespan
import discord


async def on_member_join(bot, member):
    Stats.update_server_stats(member.guild)
    await Moderation.give_member_role(member)
    log_channel = Config.get_configurated_channel(bot=bot, guild_id=member.guild.id, channel_type="status")
    if not log_channel: await Moderation.warn_no_mod_channel(guild=member.guild)
    embed_log = discord.Embed(title=f"Member joined", description=f"{member.mention} ({member.id})", color=0x5ea4ff)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar.url)
    await log_channel.send(embed=embed_log)

async def on_member_remove(bot, member):
    Stats.update_server_stats(member.guild)
    log_channel = Config.get_configurated_channel(bot=bot, guild_id=member.guild.id, channel_type="status")
    if not log_channel: await Moderation.warn_no_mod_channel(guild=member.guild)
    embed_log = discord.Embed(title=f"Member left", description=f"{member.mention} ({member.id})", color=0x995eff)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar.url)
    await log_channel.send(embed=embed_log)

async def on_voice_state_update(bot, member, before, after):
    log_channel = Config.get_configurated_channel(bot=bot, guild_id=member.guild.id, channel_type="status")
    if not log_channel: return

    changed = []
    if before.channel != after.channel:
        if after.channel:
            changed.append(f"Joined {after.channel.mention}")
        else:
            changed.append(f"Left {before.channel.mention}")
    if before.deaf != after.deaf:
        if after.deaf:
            changed.append(f"Server deafened")
        else:
            changed.append(f"Server undeafened")
    if before.mute != after.mute:
        if after.deaf:
            changed.append(f"Server muted")
        else:
            changed.append(f"Server unmuted")
    if before.requested_to_speak_at != after.requested_to_speak_at:
        if after.requested_to_speak_at:
            changed.append(f"[Stage] Requested to speak")
        else:
            changed.append(f"[Stage] Stopped requesting to speak")
    if before.self_deaf != after.self_deaf:
        if after.self_deaf:
            changed.append(f"Deafened self")
        else:
            changed.append(f"Undeafened self")
    if before.self_mute != after.self_mute:
        if after.self_mute:
            changed.append(f"Muted self")
        else:
            changed.append(f"Unmuted self")
    if before.self_stream != after.self_stream:
        if after.self_stream:
            changed.append(f"Started streaming")
        else:
            changed.append(f"Stopped streaming")
    if before.self_video != after.self_video:
        if after.self_video:
            changed.append(f"Started video")
        else:
            changed.append(f"Stopped video")
    if before.suppress != after.suppress:
        if after.suppress:
            changed.append(f"[Stage] Became suppressed")
        else:
            changed.append(f"[Stage] No longer suppressed")

    joined = "\n".join(changed)

    embed_log = discord.Embed(title=f"VC status changed", description=f"{member.mention} ({member.id})\n{joined}", color=member.color)
    embed_log.set_author(name=member.name, url=f"https://discord.com/users/{member.id}", icon_url=member.avatar.url)
    await log_channel.send(embed=embed_log)


async def on_invite_create(bot, invite):
    log_channel = Config.get_configurated_channel(bot=bot, guild_id=invite.guild.id, channel_type="status")
    if not log_channel: return

    created_user = invite.inviter
    time_remaining = format_timespan(invite.max_age)
    description = f"By {created_user.mention} ({created_user.id})\nValid for: {time_remaining} ({invite.max_uses} max uses)\nIs temporary: {invite.temporary}"

    embed_log = discord.Embed(title=f"Invite Created", description=description, color=0xf542a7)
    embed_log.set_author(name=created_user.name, url=f"https://discord.com/users/{created_user.id}", icon_url=created_user.avatar.url)
    embed_log.add_field(name="Invite Code", value=f"[{invite.code}]({invite.url})", inline=False)
    await log_channel.send(embed=embed_log)

