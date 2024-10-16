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

class Automod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="automod_enable", help="Enables automod for the server")
    @commands.has_permissions(administrator=True)
    async def automod_enable(self, ctx):
        if ctx.author.guild_permissions.administrator:
            await add_auto_mod_server(ctx.guild.id)
            await ctx.send(embed=discord.Embed(title="Automod", description="Auto mod has been enabled for this server!!!", color=discord.Color.green()))
        else:
            await ctx.send("You do not have the required permissions to use this command.")

    @commands.command(name='automod_disable', help="Removes automod from the server")
    @commands.has_permissions(administrator=True)
    async def remove_auto_mod(self, ctx):
        if ctx.author.guild_permissions.administrator:
            await remove_auto_mod_server(ctx.guild.id)
            await ctx.send("Auto moderation disabled for this server.")
        else:
            await ctx.send("You do not have the required permissions to use this command.")
            
    @app_commands.command(name="automod_enable", description="Enables auto-moderation for the server")
    @app_commands.default_permissions(administrator=True)
    async def automod_enable_slash(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            await add_auto_mod_server(interaction.guild.id)
            await interaction.response.send_message(embed=discord.Embed(title="Automod", description="Auto mod has been enabled for this server!!!", color=discord.Color.green()))
        else:
            await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)

    @app_commands.command(name="automod_disable", description="Disables auto-moderation for the server")
    @app_commands.default_permissions(administrator=True)
    async def automod_disable_slash(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator:
            await remove_auto_mod_server(interaction.guild.id)
            await interaction.response.send_message("Auto moderation disabled for this server.")
        else:
            await interaction.response.send_message("You do not have the required permissions to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Automod(bot))
