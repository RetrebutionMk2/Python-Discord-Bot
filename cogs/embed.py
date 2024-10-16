from discord.ext import commands
import discord
from discord import app_commands
import random
import datetime

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
            
            
    @app_commands.command(name="embed", description="Embed generator")
    @app_commands.describe(
        title = "Title",
        description = "Description",
        color = "Hex color code or 'random' to randomize it",
        url = "A url that the title will link to",
        footer = "Footer for the embed",
        thumbnail = "An image for thumbnail",
        image = "A url for the main image",
        channel = "Where to send embed"
    )
    async def embed_slash(
        self, interaction: discord.interactions,
        title: str,
        description: str,
        color: str,
        channel: discord.TextChannel,
        url: str = None,
        footer: str = None,
        thumbnail: str = None,
        image: str = None
        ):
        
         # Check if the user has permission to send messages in the specified channel
        if not channel.permissions_for(interaction.user).send_messages:
            await interaction.response.send_message(
                "You do not have permission to send messages in that channel.",
                ephemeral=True
            )
            return

        # Generate color
        if color.lower() == "random":
            color_int = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            color_int = discord.Color(int(color, 16))

        # Create embed
        embed = discord.Embed(title=title, description=description, color=color_int)
        
        if url:
            embed.url = url
        if footer:
            embed.set_footer(text=footer)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if image:
            embed.set_image(url=image)

        # Send embed
        await channel.send(embed=embed)
        await interaction.response.send_message(f"Embed sent successfully in {channel.mention}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Embeds(bot))
