from discord.ext import commands
import random

class coin_flip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="flip", help="Flip a coin.")
    async def flip(self, ctx):
        sides = ['heads', 'tails']
        output_side = random.choice(sides)

        await ctx.send(f"{ctx.author.mention} {output_side}")


async def setup(bot):
    await bot.add_cog(coin_flip(bot))