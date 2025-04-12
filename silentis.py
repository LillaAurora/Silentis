 import discord
from discord.ext import commands
import os

# TOKEN from environment variable (keep secure!)
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Intents setup for full server event access
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
intents.reactions = True

# Bot prefix and command setup
bot = commands.Bot(command_prefix=".", intents=intents)

# Silentis Logging Channel (set your log channel ID)
LOG_CHANNEL_ID = 1360588167681540107  # replace with your actual channel ID

# Event: On bot ready
@bot.event
async def on_ready():
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send("Silentis is now watching. 🩸")
    print(f"{bot.user} is online.")

# Event: On message (message monitoring)
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_entry = f"📨 Message from {message.author} in #{message.channel}: {message.content}"
        await log_channel.send(log_entry)

    await bot.process_commands(message)

# Command: Silent check
@bot.command()
async def silentcheck(ctx):
    await ctx.send("Your silence is measured. 🩸")

# Error logging
@bot.event
async def on_command_error(ctx, error):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"❌ Error: {str(error)}")

# Run the bot
bot.run(TOKEN)
