from discord.ext import commands
import discord
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Shows the ping of the bot")
    async def ping(self, ctx):
        actual_ping = round(self.bot.latency*1000,2)
        embed = discord.Embed(title="Pong!", description=f"{actual_ping} ms", color=discord.Color.blue())
        await ctx.send(embed=embed)
        
    @app_commands.command(name="ping", description="Gives the ping of the bot.")    
    async def ping_slash(self, interaction: discord.Interaction):
        actual_ping = round(self.bot.latency*1000,2)
        embed = discord.Embed(title="Pong!", description=f"{actual_ping} ms", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))
