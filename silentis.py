import discord
from discord.ext import commands, tasks
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Blueprint configuration (extendable from external file later)
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
        "duration_minutes": 1440,  # 24 hours
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

    # Initial Presence Ceremony
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

    # Whisperer Promotion
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

    # Echoed Recognition
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

# Tribute system integration (manual or API-based placeholder)
async def handle_tribute(user, amount):
    bp = blueprints["tribute_advancement"]
    if amount >= bp["amount_threshold"]:
        for guild in bot.guilds:
            member = guild.get_member(user.id)
            if member:
                role = discord.utils.get(guild.roles, name=bp["role_to_assign"])
                if role and role not in member.roles:
                    await member.add_roles(role)
                    log_channel = discord.utils.get(guild.channels, name=bp["log_channel"])
                    if log_channel:
                        await log_channel.send(f"{member.mention} was moved via tribute (💠).")
                break

# Collective Stillness Ritual
async def start_collective_stillness():
    bp = blueprints["collective_stillness"]
    bp["active"] = True
    bp["start_time"] = discord.utils.utcnow()
    log_channel = discord.utils.get(bot.get_all_channels(), name=bp["log_channel"])
    if log_channel:
        await log_channel.send("🌑 Collective Stillness Ritual has begun.")
    # Lock channels here (not implemented)
    await asyncio.sleep(bp["duration_minutes"] * 60)
    bp["active"] = False
    # Unlock channels here (not implemented)
    if log_channel:
        await log_channel.send("🌕 Collective Stillness Ritual has ended.")

# Ritual Structure Audit — Only usable by Lilla
@bot.command(name="structure-audit")
async def structure_audit(ctx):
    LILLA_ID = 1358577229638013020

    if ctx.author.id != LILLA_ID:
        return  # Only Lilla can use this

    guild = ctx.guild
    log_channel = discord.utils.get(guild.text_channels, name="silenta-logbook")
    if not log_channel:
        await ctx.send("⚠️ Log channel (#silenta-logbook) not found.")
        return

    await log_channel.send("🔎 **SERVER AUDIT INITIATED**")

    required_roles = ["Silent", "Whisperer", "Echoed", "Bound", "Exiled"]
    missing_roles = [role for role in required_roles if not discord.utils.get(guild.roles, name=role)]

    if missing_roles:
        await log_channel.send(f"⚠️ Missing roles: {', '.join(missing_roles)}")
    else:
        await log_channel.send("✅ All ceremonial roles are present.")

    required_channels = [
        "main-hall", "rituals-and-rules", "whispers",
        "echo-chambers", "tribute-menu", "public-protocols", "silenta-logbook"
    ]
    missing_channels = [ch for ch in required_channels if not discord.utils.get(guild.channels, name=ch)]

    if missing_channels:
        await log_channel.send(f"⚠️ Missing channels: {', '.join(missing_channels)}")
    else:
        await log_channel.send("✅ All essential channels are present.")

    me = guild.me
    required_perms = ["manage_roles", "read_messages", "send_messages", "add_reactions"]
    perms = me.guild_permissions
    missing_perms = [perm for perm in required_perms if not getattr(perms, perm)]

    if missing_perms:
        await log_channel.send(f"⚠️ Silentis is missing permissions: {', '.join(missing_perms)}")
    else:
        await log_channel.send("✅ Silentis has all required permissions.")

    await log_channel.send("🕊 **Audit complete. Structure holds — or reveals its weakness.**")

# Run the bot (token must be kept secret in deployment)
bot.run("MTM2MDYxODI4ODE3NDA3MjA0OQ.GAns50.I--1gwimEmxS_3clvZ5y5jm_AIczyVFoJtXiLY")



