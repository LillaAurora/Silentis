import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True
intents.reactions = True

# Bot initialization
bot = commands.Bot(command_prefix=".", intents=intents)

# Log channel ID (replace with actual ID)
LOG_CHANNEL_ID = 123456789012345678  # Replace with your log channel ID

@bot.event
async def on_ready():
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send("Silentis is now active and watching. 🩸")
    print(f"{bot.user} is online.")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        log_entry = f"📨 Message from {message.author} in #{message.channel}: {message.content}"
        await log_channel.send(log_entry)

    await bot.process_commands(message)

@bot.command()
async def silentcheck(ctx):
    await ctx.send("Your silence is being measured. 🩸")

@bot.event
async def on_command_error(ctx, error):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"❌ Error: {str(error)}")

bot.run(TOKEN)