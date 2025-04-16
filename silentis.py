import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Restrict command usage to control-chamber only
ALLOWED_COMMAND_CHANNEL = "control-chamber"

# Blueprint configuration
blueprints = {
    "initial_presence": {
        "reaction": "🔧",  # 🕯
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

async def handle_tribute(user, amount):
    bp = blueprints["tribute_advancement"]
    if amount >= bp["amount_threshold"]:
        guild = discord.utils.get(bot.guilds, name="YourServerName")
        member = guild.get_member(user.id)
        role = discord.utils.get(guild.roles, name=bp["role_to_assign"])
        if role and role not in member.roles:
            await member.add_roles(role)
            log_channel = discord.utils.get(guild.channels, name=bp["log_channel"])
            if log_channel:
                await log_channel.send(f"{member.mention} was moved via tribute (💠).")

async def start_collective_stillness():
    bp = blueprints["collective_stillness"]
    bp["active"] = True
    bp["start_time"] = discord.utils.utcnow()
    log_channel = discord.utils.get(bot.get_all_channels(), name=bp["log_channel"])
    if log_channel:
        await log_channel.send("🌑 Collective Stillness Ritual has begun.")

    await asyncio.sleep(bp["duration_minutes"] * 60)
    bp["active"] = False
    if log_channel:
        await log_channel.send("🌕 Collective Stillness Ritual has ended.")

# Command use restriction wrapper
def command_channel_only():
    async def predicate(ctx):
        return ctx.channel.name == ALLOWED_COMMAND_CHANNEL
    return commands.check(predicate)

# Ritual Structure Audit — Only usable by Lilla
@bot.command(name="structure-audit")
@command_channel_only()
async def structure_audit(ctx):
    LILLA_ID = 1358577229638013020
    if ctx.author.id != LILLA_ID:
        return

    required_channels = [
        "how-to-interact", "main-hall", "rituals-and-rules", "whispers",
        "echo-chambers", "questions-to-silence", "tribute-menu",
        "public-protocols", "protection-archive", "control-chamber"
    ]
    guild = ctx.guild
    existing_channels = [channel.name for channel in guild.channels]
    missing = [c for c in required_channels if c not in existing_channels]

    embed = discord.Embed(title="📂 STRUCTURE AUDIT REPORT")
    if not missing:
        embed.description = "✅ All required channels are present. Structure is intact."
    else:
        embed.description = "❌ Missing channels: " + ", ".join(missing)
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
