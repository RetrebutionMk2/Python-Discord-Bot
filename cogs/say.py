from discord.ext import commands
import discord
from discord import app_commands
import random

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      
    @commands.command(help="Say something using the bot. Format: $say [text channel] [text]")
    async def say(self, ctx, channel: discord.TextChannel, *, message: str):
        if channel.permissions_for(ctx.author).send_messages:
            try:
                await channel.send(message)
                await ctx.send(f"Message sent to {channel.mention}")
            except discord.Forbidden:
                await ctx.send("Could not send the message. Check if the bot has permissions to send messages in that channel.")
        else:
            await ctx.send("You don't have permissions to use this command.")


    @app_commands.command(name="say", description="Make me say something")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(
        thing_to_say = "What should I say?",
        target_channel = "Select the channel where the message should be sent."
        )
    async def say_slash(self, interaction: discord.interactions, target_channel: discord.TextChannel, thing_to_say: str):
        await target_channel.send(thing_to_say)
        await interaction.response.send_message(f"Message sent successfully in {target_channel.mention}.", ephemeral = True)


async def setup(bot):
    await bot.add_cog(Say(bot))