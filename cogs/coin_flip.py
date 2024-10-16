from discord.ext import commands
from discord import app_commands
import discord
import random

class coin_flip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    global random_color
    random_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
    @commands.command(name="coinflip", help="Flip a coin.", aliases=["flip"])
    async def flip(self, ctx):
        sides = ['heads', 'tails']
        output_side = random.choice(sides)

        await ctx.send(f"{ctx.author.mention} {output_side}")
        
    @app_commands.command(name="coinflip", description="Flip a coin, see your chances.")
    async def flip_slash(self, interaction: discord.Interaction):
        sides = ['heads', 'tails']
        output_side = random.choice(sides)
        embed = discord.Embed(title=f"{output_side}!!!", color=random_color)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(coin_flip(bot))
