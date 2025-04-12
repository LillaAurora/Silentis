import discord
from discord.ext import commands
import os

# Token from environment variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Intents for full server visibility
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
intents.reactions = True

# Bot setup
bot = commands.Bot(command_prefix=".", intents=intents)

# Log channel (actual ID set)
LOG_CHANNEL_ID = 1360588167681540107

# On bot ready
@bot.event
async def on_ready():
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send("Silentis is present. Watching. 🩸")
    print(f"{bot.user} is now online.")

# On message
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_entry = f"📨 {message.author} in #{message.channel}: {message.content}"
        await log_channel.send(log_entry)

    await bot.process_commands(message)

# Silent check command
@bot.command()
async def silentcheck(ctx):
    await ctx.send("Your silence is measured. 🩸")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"❌ Error: {str(error)}")

# Run bot
bot.run(TOKEN)
