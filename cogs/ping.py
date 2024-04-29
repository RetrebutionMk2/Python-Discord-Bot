from discord.ext import commands
import discord

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="$", intents=intents)

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Shows the ping of the bot")
    async def ping(self, ctx):
        actual_ping = round(self.bot.latency*1000,2)
        embed = discord.Embed(title="Pong!", description=f"{actual_ping} ms", color=discord.Color.blue())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))