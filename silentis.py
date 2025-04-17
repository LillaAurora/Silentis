import discord
from discord.ext import commands
from datetime import datetime
import os
import dotenv

dotenv.load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = 1360588167681540107  # 🔐 Lilla privát logcsatornája

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# 📜 Stilizált napló
async def stylized_log(event_type: str, content: str, channel_name: str, user: discord.User):
    now = datetime.utcnow()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S UTC")
    date_str = now.strftime("%Y-%m-%d")
    log_dir = "data/logs"
    log_file = f"{log_dir}/{date_str}.txt"

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Fájlba mentés
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] [{event_type}] in #{channel_name} | {user}: {content}\n")

    # Discord logüzenet
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        discord_message = (
            f"🌘 **{event_type}** in `#{channel_name}`\n"
            f"🧍 **User**: {user.mention}\n"
            f"{content}\n"
            f"🕰 {timestamp}"
        )
        await log_channel.send(discord_message)

# 💬 Üzenet érkezése
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    content = f"💬 *Message*: “{message.content}”"
    await stylized_log("Whisper Entered", content, message.channel.name, message.author)
    await bot.process_commands(message)

# 📝 Üzenetszerkesztés
@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    content = (
        f"🔁 *Edited Whisper*\n"
        f"📜 Before: “{before.content}”\n"
        f"📜 After:  “{after.content}”"
    )
    await stylized_log("Echo Shifted", content, before.channel.name, before.author)

# 🗑️ Üzenettörlés
@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    content = f"💀 *Deleted Whisper*: “{message.content}”"
    await stylized_log("Echo Vanished", content, message.channel.name, message.author)

# 🔔 Csatlakozás
@bot.event
async def on_member_join(member):
    content = f"🌕 *A soul has entered.*"
    await stylized_log("Presence Felt", content, "—", member)

# 🕯 Távozás
@bot.event
async def on_member_remove(member):
    content = f"🌑 *The silence reclaimed one.*"
    await stylized_log("Presence Faded", content, "—", member)

# 🎭 Becenév vagy névváltozás
@bot.event
async def on_user_update(before, after):
    if before.name != after.name:
        content = f"🖋 *Username changed*\nFrom: `{before.name}` → To: `{after.name}`"
        await stylized_log("Name Shifted", content, "—", after)

# 🎗 Szerepkör változás
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        added = [r.name for r in after.roles if r not in before.roles]
        removed = [r.name for r in before.roles if r not in after.roles]
        changes = ""
        if added:
            changes += f"➕ Gained: {', '.join(added)}\n"
        if removed:
            changes += f"➖ Lost: {', '.join(removed)}"
        if changes:
            await stylized_log("Role Shifted", changes, "—", after)

# 🔊 Voice csatorna események
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        if after.channel and not before.channel:
            content = f"🔊 Joined voice: `{after.channel.name}`"
            await stylized_log("Echo Heard", content, after.channel.name, member)
        elif before.channel and not after.channel:
            content = f"🔇 Left voice: `{before.channel.name}`"
            await stylized_log("Echo Silenced", content, before.channel.name, member)
        else:
            content = f"🔄 Moved voice: `{before.channel.name}` → `{after.channel.name}`"
            await stylized_log("Echo Shifted", content, after.channel.name, member)

# 🧱 Csatornaváltozások (új, törölt, módosított)
@bot.event
async def on_guild_channel_create(channel):
    content = f"➕ *Channel created*: `#{channel.name}`"
    await stylized_log("Domain Expanded", content, channel.name, channel.guild.me)

@bot.event
async def on_guild_channel_delete(channel):
    content = f"➖ *Channel deleted*: `#{channel.name}`"
    await stylized_log("Domain Collapsed", content, channel.name, channel.guild.me)

@bot.event
async def on_guild_channel_update(before, after):
    if before.name != after.name:
        content = f"📝 *Channel renamed*\nFrom: `#{before.name}` → To: `#{after.name}`"
        await stylized_log("Domain Renamed", content, after.name, after.guild.me)

# ✅ Indulás
@bot.event
async def on_ready():
    print(f"Silentis awakened as {bot.user}")

bot.run(TOKEN)
