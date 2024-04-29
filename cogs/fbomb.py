from discord.ext import commands
import discord

class FBomb(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fbomb", help="Drop the F-Bomb on someone")
    async def fbomb(self, ctx, member: discord.Member):
        await ctx.message.delete()
        await ctx.send(f"Fuck you {member.mention}")
    
async def setup(bot):
    await bot.add_cog(FBomb(bot))