from discord.ext import commands
import discord
import random

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help="Send an embed to a channel. Format: $embed [title] [description] [color hex, type random / r to randomize it] [channel]\n Note: Use "" to seperate title and description ")
    async def embed(self, ctx, title: str, description: str, color: str, channel: discord.TextChannel):
        if channel.permissions_for(ctx.author).send_messages:
            try:

                if color.lower() == "r" or color.lower() == "random":
                    color_int = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

                else:
                    color_int = discord.Color(int(color, 16))
                
                embed = discord.Embed(title=title, description=description, color=color_int)

                send_channel = channel or ctx.channel
                await send_channel.send(embed=embed)
                await ctx.send(f"Embed sent to {send_channel.mention}.")
            
            except discord.Forbidden:
                await ctx.send("Cannot send message in the specified channel. Please check if the bot has desired permissions.")
        else:
            await ctx.send("You don't have permissions to use this command.")


async def setup(bot):
    await bot.add_cog(Embeds(bot))