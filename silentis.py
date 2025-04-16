import discord
from discord.ext import commands, tasks
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Blueprint configuration
blueprints = {
    "initial_presence": {
        "reaction": "🕯",
        "channel": "rituals-and-rules",
        "role_to_assign": "Silent",
        "log_channel": "silenta-logbook",
        "dm_message": "You moved without speaking. You earned your first silence."
    },
    "tribute_advancement": {
        "amount_threshold": 50,
        "role_to_assign": "Bound",
        "log_channel": "silenta-logbook"
    },
    "collective_stillness": {
        "start_time": None,
        "duration_minutes": 1440,
        "active": False,
        "log_channel": "silenta-logbook"
    },
    "whisperer_promotion": {
        "role_check": "Silent",
        "role_to_assign": "Whisperer",
        "activity_channel": "whispers",
        "log_channel": "silenta-logbook"
    },
    "echoed_recognition": {
        "role_check": "Whisperer",
        "role_to_assign": "Echoed",
        "activity_channel": "echo-chambers",
        "log_channel": "silenta-logbook"
    }
}

@bot.event
async def on_ready():
    print(f"Silentis active as {bot.user}")

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    channel = bot.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = payload.member

    bp = blueprints["initial_presence"]
    if str(payload.emoji) == bp["reaction"] and channel.name == bp["channel"]:
        role = discord.utils.get(guild.roles, name=bp["role_to_assign"])
        if role and role not in member.roles:
            await member.add_roles(role)
            log_channel = discord.utils.get(guild.channels, name=bp["log_channel"])
            if log_channel:
                await log_channel.send(f"{member.mention} completed the Initial Presence Ceremony.")
            try:
                await member.send(bp["dm_message"])
            except:
                pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    bp = blueprints["whisperer_promotion"]
    if message.channel.name == bp["activity_channel"]:
        guild = message.guild
        role_check = discord.utils.get(guild.roles, name=bp["role_check"])
        role_assign = discord.utils.get(guild.roles, name=bp["role_to_assign"])
        if role_check in message.author.roles and role_assign not in message.author.roles:
            await message.author.add_roles(role_assign)
            log_channel = discord.utils.get(guild.channels, name=bp["log_channel"])
            if log_channel:
                await log_channel.send(f"{message.author.mention} promoted to Whisperer.")

    bp = blueprints["echoed_recognition"]
    if message.channel.name == bp["activity_channel"]:
        guild = message.guild
        role_check = discord.utils.get(guild.roles, name=bp["role_check"])
        role_assign = discord.utils.get(guild.roles, name=bp["role_to_assign"])
        if role_check in message.author.roles and role_assign not in message.author.roles:
            await message.author.add_roles(role_assign)
            log_channel = discord.utils.get(guild.channels, name=bp["log_channel"])
            if log_channel:
                await log_channel.send(f"{message.author.mention} has been Echoed.")

    await bot.process_commands(message)

@bot.command(name="permission-audit")
async def permission_audit(ctx):
    LILLA_ID = 1358577229638013020
    if ctx.author.id != LILLA_ID:
        return

    guild = ctx.guild
    log_channel = discord.utils.get(guild.text_channels, name="silenta-logbook")
    if not log_channel:
        return

    await log_channel.send("🔐 **PERMISSION AUDIT INITIATED**")

    target_roles = ["Silent", "Whisperer", "Echoed", "Bound", "Exiled"]
    key_channels = ["main-hall", "rituals-and-rules", "whispers", "echo-chambers"]
    anomalies = []

    for ch_name in key_channels:
        ch = discord.utils.get(guild.text_channels, name=ch_name)
        if not ch:
            continue
        for role_name in target_roles:
            role = discord.utils.get(guild.roles, name=role_name)
            if not role:
                continue
            perms = ch.permissions_for(role)
            if role_name == "Silent" and ch_name == "whispers" and not perms.send_messages:
                anomalies.append(f"❌ Silent cannot write in #{ch_name} (should be able to)")
            if role_name == "Whisperer" and ch_name == "echo-chambers" and not perms.read_messages:
                anomalies.append(f"❌ Whisperer cannot view #{ch_name} (should be able to)")
            if role_name == "Echoed" and ch_name == "echo-chambers" and not perms.send_messages:
                anomalies.append(f"❌ Echoed cannot write in #{ch_name} (should be able to)")
            if role_name == "Bound" and perms.read_messages:
                anomalies.append(f"⚠️ Bound can view #{ch_name} (should be hidden)")
            if role_name == "Exiled" and perms.read_messages:
                anomalies.append(f"⚠️ Exiled can view #{ch_name} (should be hidden)")

    if anomalies:
        await log_channel.send("\n".join(anomalies))
    else:
        await log_channel.send("✅ All permissions aligned with protocol.")

    await log_channel.send("🔒 **Permission audit complete. Structure holds.**")

import os
bot.run(os.getenv("DISCORD_TOKEN"))

