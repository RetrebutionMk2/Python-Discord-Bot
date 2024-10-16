import discord
from discord.ext import commands
from discord import app_commands
from badwords import get_badwords_data
from auto_mod import add_auto_mod_server, is_auto_mod_active, remove_auto_mod_server
import string
import os
import json


# Load the data from the JSON file or create a new dictionary if the file doesn't exist
if os.path.exists('oil_react_settings.json'):
    with open('oil_react_settings.json', 'r') as f:
        oil_react_settings = json.load(f)
else:
    oil_react_settings = {}
    
if os.path.exists('personal_oil_react_settings.json'):
    with open('personal_oil_react_settings.json', 'r') as f:
        personal_oil_react_settings = json.load(f)

else:
    personal_oil_react_settings = {}



class message(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            pass

        if "$" in message.content:
            pass

        if message.guild is None:
            pass

        # AUTOMOD
        server_id = message.guild.id
        badwords_data = await get_badwords_data()
        badwords = badwords_data["bad_words"]

        if await is_auto_mod_active(server_id):
            message_content_cleaned = ''.join(char for char in message.content if char not in string.punctuation)
            words = message_content_cleaned.split()

            for word in words:
                if word in badwords:
                    await message.delete()
                    bad_word_embed = discord.Embed(title=f"{message.author}, Hey! That word is not allowed here!", color=discord.Color.red())
                    await message.channel.send(embed=bad_word_embed)
                    break

        guild_id = str(message.guild.id)

        # Check if the OIL REACTION feature is enabled in this server and in the correct channel
        if guild_id in oil_react_settings:
            channel_id = oil_react_settings[guild_id]["channel_id"]
            # Check if the message is in the correct channel and contains one of the keywords
            keywords = ["oil", "diesel", "petrol", "kerosene", 'fuel', 'gas']
            if message.channel.id == channel_id and any(word in message.content.lower() for word in keywords):
                await message.add_reaction("🛢️")
                
        # Check if the PERSONAL OIL REACTION is enabled
        for user in message.mentions:
            user_id = str(user.id)
            if user_id in personal_oil_react_settings:
                await message.add_reaction("🛢️")
                break

        # Ensure commands still work
        await self.bot.process_commands(message)
        

async def setup(bot):
    await bot.add_cog(message(bot))
