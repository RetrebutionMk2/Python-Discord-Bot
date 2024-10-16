from discord.ext import commands
import discord
import random
from discord import app_commands

class lockdown(commands.Cog):
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
        await channel.set_permissions(
    ctx.guild.default_role,
    send_messages=False,
    send_tts_messages=False,
    manage_messages=False,
    embed_links=False,
    attach_files=False,
    read_message_history=False,
    mention_everyone=False,
    external_emojis=False,
    connect=False,
    speak=False,
    mute_members=False,
    deafen_members=False,
    move_members=False,
    use_vad=False
)


        await ctx.send(embed=discord.Embed(title="Channel locked down ✅", color=random_color))
        
    @app_commands.command(name="lockdown", description="Locks down a channel.")
    @app_commands.default_permissions(manage_channels = True)
    async def lockdown_slash(self, interaction: discord.Interaction):        
        channel = interaction.channel

        try:
            await channel.set_permissions(
    interaction.guild.default_role,
    send_messages=False,
    send_tts_messages=False,
    manage_messages=False,
    embed_links=False,
    attach_files=False,
    read_message_history=False,
    mention_everyone=False,
    external_emojis=False,
    connect=False,
    speak=False,
    mute_members=False,
    deafen_members=False,
    move_members=False,
    use_vad=False
)

            await interaction.response.send_message(
                embed=discord.Embed(title="Channel locked down ✅", color=random_color)
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(title="An error occurred", description=str(e), color=random_color)
            )
        

    @commands.command(name="unlock", help="Lift lockdown.")
    @commands.has_permissions(manage_channels = True)
    async def unlock(self, ctx):
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send(embed=discord.Embed(title="You don't have necessary permissions to use this command", color=random_color))
            return
        
        channel = ctx.channel

        await channel.set_permissions(
    ctx.guild.default_role,
    send_messages=True,
    send_tts_messages=True,
    manage_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    mention_everyone=True,
    external_emojis=True,
    connect=True,
    speak=True,
    mute_members=True,
    deafen_members=True,
    move_members=True,
    use_vad=True
)


        await ctx.send(embed=discord.Embed(title="Channel unlocked ✅", color=random_color))
        
    @app_commands.command(name="unlock", description="Lifts the lockdown on a channel.")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock_slash(self, interaction: discord.Interaction):        
        channel = interaction.channel

        try:
            # Re-enable sending messages for the default role (everyone)
            await channel.set_permissions(
    interaction.guild.default_role,
    send_messages=True,
    send_tts_messages=True,
    manage_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    mention_everyone=True,
    external_emojis=True,
    connect=True,
    speak=True,
    mute_members=True,
    deafen_members=True,
    move_members=True,
    use_vad=True
)

            await interaction.response.send_message(
                embed=discord.Embed(title="Channel unlocked ✅", color=random_color)
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(title="An error occurred", description=str(e), color=random_color)
            )


async def setup(bot):
    await bot.add_cog(lockdown(bot))
