from discord.ext import commands
import discord
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True
bot = commands.Bot(command_prefix='$', intents=intents)


class Spam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spam", help="Spam something in #spam. Format: $spam [amount] [content]")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def spam(self, ctx, amount: int, *, content: str):
        spam_channel_name = "spam"
        channel = discord.utils.get(ctx.guild.channels, name=spam_channel_name)

        if amount > 100:
            await ctx.send("Amount cannot be above 100.")
            return

        if channel is None:
            await ctx.send("#spam is not available. Please ask one of the moderators to assist you with this.")
            return

        try:
            for _ in range(amount):
                await channel.send(content)
                await asyncio.sleep(0.2)
        except commands.CommandOnCooldown as e:
            remaining_time = round(e.retry_after, 2)
            await ctx.send(f"You are on cooldown. Please wait {remaining_time} seconds before using this command again.")
            

async def setup(bot):
    await bot.add_cog(Spam(bot))