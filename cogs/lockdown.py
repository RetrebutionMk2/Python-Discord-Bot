from discord.ext import commands
import discord
import random

class Lockdown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    global random_color
    random_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    @commands.command(name="lockdown", help="Locks down a channel.")
    @commands.has_permissions(manage_channels = True)
    async def lockdown(self, ctx):
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send(embed=discord.Embed(title="You don't have necessary permissions to use this command", color=random_color))
            return
        
        channel = ctx.channel

        await channel.set_permissions(ctx.guild.default_role, send_messages = False)

        await ctx.send(embed=discord.Embed(title="Channel locked down ✅", color=random_color))

    @commands.command(name="unlock", help="Lift lockdown.")
    @commands.has_permissions(manage_channels = True)
    async def unlock(self, ctx):
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send(embed=discord.Embed(title="You don't have necessary permissions to use this command", color=random_color))
            return
        
        channel = ctx.channel

        await channel.set_permissions(ctx.guild.default_role, send_messages = True)

        await ctx.send(embed=discord.Embed(title="Channel unlocked ✅", color=random_color))


async def setup(bot):
    await bot.add_cog(Lockdown(bot))