import discord
from discord.ext import commands
from discord import app_commands
import json
import os

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


# Function to save the settings to a JSON file
def save_settings():
    with open('oil_react_settings.json', 'w') as f:
        json.dump(oil_react_settings, f, indent=4)
        
def save_personal_reaction_settings():
    with open('personal_oil_react_settings.json', 'w') as f:
        json.dump(personal_oil_react_settings, f, indent=4)

class OilReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to toggle the oil reaction setup (Prefix Command)
    @commands.command(name='oilreactsetup')
    @commands.has_permissions(manage_channels=True)  # Only allow users with manage channels permission
    async def oilreactsetup(self, ctx):
        guild_id = str(ctx.guild.id)

        # Toggle the setting
        if guild_id in oil_react_settings:
            del oil_react_settings[guild_id]
            await ctx.send("Oil reaction has been disabled.")
        else:
            oil_react_settings[guild_id] = {"enabled": True, "channel_id": ctx.channel.id}
            await ctx.send(f"Oil reaction has been enabled in {ctx.channel.mention}.")

        # Save the updated settings to the JSON file
        save_settings()

    # Slash Command to toggle the oil reaction setup
    @app_commands.command(name="oilreactsetup", description="Enable or disable oil reactions in this channel")
    @app_commands.default_permissions(manage_messages=True)  # Only allow users with manage messages permission
    async def oilreactsetup_slash(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)

        # Check if the user has permission to manage messages
        if interaction.user.guild_permissions.manage_messages:
            # Toggle the setting
            if guild_id in oil_react_settings:
                del oil_react_settings[guild_id]
                await interaction.response.send_message("Oil reaction has been disabled.", ephemeral=True)
            else:
                oil_react_settings[guild_id] = {"enabled": True, "channel_id": interaction.channel.id}
                await interaction.response.send_message(f"Oil reaction has been enabled in {interaction.channel.mention}.", ephemeral=True)

            # Save the updated settings to the JSON file
            save_settings()
        else:
            # If the user doesn't have permission
            await interaction.channel.send("You do not have permission to manage messages.", ephemeral=True)

    @commands.command(name="personaloilreact", help="Reacts with 🛢️ when someone pings you")
    async def personaloilreact(self, ctx):
        user_id = str(ctx.author.id)
        username = ctx.author.name
        if user_id in personal_oil_react_settings:
            del personal_oil_react_settings[user_id]
            await ctx.send("Personal Oil Reaction Disabled")
        else:
            personal_oil_react_settings[user_id] = True
            await ctx.send("Personal Oil Reaction Enabled")

        save_personal_reaction_settings()

    @app_commands.command(name="personaloilreact", description="Reacts with 🛢️ when someone pings you")
    async def personaloilreact_slash(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        username = interaction.user.name
        if user_id in personal_oil_react_settings:
            del personal_oil_react_settings[user_id]
            await interaction.response.send_message("Personal Oil Reaction Disabled")
        else:
            personal_oil_react_settings[user_id] = True
            await interaction.response.send_message("Personal Oil Reaction Enabled")

        save_personal_reaction_settings()


# Add the cog to the bot
async def setup(bot):
    await bot.add_cog(OilReact(bot))
