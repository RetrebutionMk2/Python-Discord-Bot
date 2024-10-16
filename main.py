import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True

bot = commands.Bot(command_prefix='$', intents=intents)

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
            except Exception as e:
                print(e)

@bot.event
async def on_ready():
    try: 
        print(f'We have logged in as {bot.user}')
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('Farming Oil\n Prefix: $'))
        
        await load_extensions()
    
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    
    except Exception as e:
        print(f"Error in on_ready {e}")

try:
    token = os.getenv('DISCORD_TOKEN')
    if token == "":
        raise Exception("Please add your token to the Secrets pane.")
    bot.run(token)
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e
