from discord.ext import commands
import discord
import asyncio
import random
import json
from typing import Union

CASE_FILE_PATH = "./cogs/case_ids.json"

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_case_ids()

    def load_case_ids(self):
        try:
            with open(CASE_FILE_PATH, "r") as file:
                self.case_ids = json.load(file)
        except FileNotFoundError:
            self.case_ids = {}  # Initialize as an empty dictionary if file not found
        except json.JSONDecodeError:
            self.case_ids = {}  # Initialize as an empty dictionary if JSON decode error

        for case_id, data in self.case_ids.items():
            data["user_id"] = int(data["user_id"])

    def save_case_ids(self):
        with open(CASE_FILE_PATH, "w") as file:
            # Convert user IDs from str to int before saving
            json.dump({case_id: {"user_id": int(data["user_id"]), "reason": data["reason"]} for case_id, data in self.case_ids.items()}, file, indent=4)


    global random_color
    random_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    @commands.command(name="purge", help="To bulk delete messages")
    async def purge(self, ctx, amount: int):
        if ctx.author.guild_permissions.manage_messages:
            try:
                await ctx.channel.purge(limit=amount+1)
                await ctx.send(embed=discord.Embed(title="Purge", description=f"{amount} messages deleted.", color=random_color))
            except discord.Forbidden:
                await ctx.send("I don't have permissions to delete messages.")
        else:
            await ctx.send("You don't have permissiions to use this command.")

        # Log the action
        channel = discord.utils.get(ctx.guild.text_channels, name="oil-logs")
        if channel:
            embed = discord.Embed(title="Purgecommand used",
                                description=f"Purge command used by {ctx.author.mention}",
                                color=discord.Color.red())
            embed.add_field(name="Amount", value=amount, inline=False)
            await channel.send(embed=embed)


    @commands.command(help="Timeout a member")
    @commands.has_permissions(manage_channels=True)
    async def timeout(self, ctx, member: discord.Member, duration: int):
        # Ensure duration is positive
        if duration <= 0:
            await ctx.send("Duration must be greater than 0 minutes.")
            return
        
        timeout_seconds = duration * 60  # Convert minutes to seconds
        
        # Attempt to timeout the member using the API
        try:
            await member.timeout(timeout_seconds)  # Timeout the member
            await ctx.send(embed=discord.Embed(title="Timeout", description=f"{member.mention} has been timed out for {duration} minute(s).", color=random_color))
            
            # Log the action
            channel = discord.utils.get(ctx.guild.text_channels, name="oil-logs")
            if channel:
                embed = discord.Embed(title="Member Timed out",
                                    description=f"{member.mention} has been timed out by {ctx.author.mention}",
                                    color=discord.Color.red())
                await channel.send(embed=embed)
        
        except discord.Forbidden:
            await ctx.send("I don't have the necessary permissions to timeout this member.")
        except discord.HTTPException as e:
            await ctx.send(f"An error occurred: {e}")


    @commands.command(help="Mute a member")
    async def mute(self, ctx, member: discord.Member, duration: int):
        """Mute a member for a specified duration"""
        # Check if the author of the command has permission to manage roles
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You don't have permission to manage roles.")
            return

        # Get the muted role or create it if it doesn't exist
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="Muted")

            # Set permissions for text channels
            for channel in ctx.guild.text_channels:
                if channel.name != "appeals":
                    await channel.set_permissions(muted_role, send_messages=False)

        # Set permissions for the appeals channel
        appeals_channel = discord.utils.get(ctx.guild.channels, name="appeals")
        if appeals_channel:
            await appeals_channel.set_permissions(muted_role, send_messages=True)

        # Assign the muted role to the member
        await member.add_roles(muted_role)
        await ctx.send(embed=discord.Embed(title="Mute", description=f"{member.mention} has been muted for {duration} minutes.", color=random_color))

        # Log the action
        channel = discord.utils.get(ctx.guild.text_channels, name="oil-logs")
        if channel:
            embed = discord.Embed(title="Member Muted",
                                description=f"{member.mention} has been muted by {ctx.author.mention}",
                                color=discord.Color.red())
            await channel.send(embed=embed)

        # Wait for the duration
        await asyncio.sleep(duration * 60)

        # Remove the muted role after the duration
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} has been unmuted.")



    @commands.command(help="Unmute a member")
    async def unmute(self, ctx, member: discord.Member):
        # Check if the user has the necessary permissions to execute this command
        if ctx.author.guild_permissions.manage_roles:
            # Get the muted role from the server
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if muted_role is None:
                await ctx.send("Muted role not found. Make sure you have a role named 'Muted'.")
                return

            # Remove the muted role from the member
            try:
                await member.remove_roles(muted_role, reason="Unmuted")
                await ctx.send(f"{member.mention} has been unmuted.")
            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to manage roles.")
        else:
            await ctx.send("You don't have the necessary permissions to use this command.")


    @commands.command(help="Ban a member")
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        # Check if the user has the necessary permissions to execute this command
        if ctx.author.guild_permissions.ban_members:
            # Attempt to ban the member
            try:
                await member.ban(reason=reason)
                await ctx.send(embed=discord.Embed(title="BAN", description=f"**{member.mention} has been banned.**", color=random_color))
                
                channel = discord.utils.get(ctx.guild.text_channels, name="oil-logs")
                if channel:
                    embed = discord.Embed(title="Member Banned",
                                        description=f"{member.mention} has been banned by {ctx.author.mention}",
                                        color=discord.Color.red())
                    embed.add_field(name="Reason", value=reason, inline=False)
                    await channel.send(embed=embed)
                    
                    
            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to ban members.")
        else:
            await ctx.send("You don't have the necessary permissions to use this command.")


    @commands.command(help="Unban a member")
    async def unban(self, ctx, userId: int, *, reason=None):
        if ctx.author.guild_permissions.ban_members:
            try:
                await ctx.guild.unban(user=discord.Object(id=userId), reason=reason)  # Use discord.Object for unban
                await ctx.send("User unbanned.")
            except discord.Forbidden:
                await ctx.send("I don't have the necessary permissions to ban members.")
        else:
            await ctx.send("You don't have the necessary permissions to use this command.")



    @commands.command(help="Warn a member")
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        if ctx.author.guild_permissions.manage_roles:
            case_id = self.generate_case_id()
            self.case_ids[case_id] = {"user_id": member.id, "reason": reason}
            self.save_case_ids()
            embed = discord.Embed(title='Warn', description=f'{member.display_name} has been warned.\n Reason: {reason} \n Case id = {case_id}', color=random_color)
            try:
                await member.send(embed=embed)
                await ctx.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("I don't have necessary permissions to warn members.")
        else:
            await ctx.send("You don't have necessary permissions to use this command.")


        # Log the action
        channel = discord.utils.get(ctx.guild.text_channels, name="oil-logs")
        if channel:
            embed = discord.Embed(title="Member Warned",
                                description=f"{member.mention} has been warned by {ctx.author.mention}",
                                color=discord.Color.red())
            embed.add_field(name="Reason", value=reason, inline=False)
            await channel.send(embed=embed)


    def generate_case_id(self):
        while True:
            case_id = ''.join(random.choices('0123456789', k=5))
            if not case_id in self.case_ids:
                return case_id
            
    @commands.command(help="Check details of a case.")
    async def case_id(self, ctx, case_id:str):
        if ctx.author.guild_permissions.manage_nicknames:
            self.load_case_ids()
            if case_id in self.case_ids:
                member_id, reason = self.case_ids[case_id]["user_id"], self.case_ids[case_id]["reason"]
                member = ctx.guild.get_member(member_id)
                if member:
                    embed = discord.Embed(title=f"Case {case_id}", description=f"Member: {member.display_name} \n Reason: {reason if reason else 'No reason provided'}", color=random_color)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title=f"Case {case_id}",description=f"Member: {member.display_name} \nReason: {reason if reason else 'No reason provided'}", color=random_color)
                    await ctx.send(embed=embed)
            else:
                await ctx.send(embed = discord.Embed(title=f"Case {case_id}", description=f"Case not found", color = random_color))
        else:
            await ctx.send("You don't have necessary permissions to use this command.")

    @commands.command(help="Get all the list of cases in the server.")
    async def server_cases(self, ctx):
        if ctx.author.guild_permissions.manage_nicknames:
            self.load_case_ids()
            all_case_ids = self.case_ids
            embed = discord.Embed(title="Case IDs", color=random_color)
            for i, case_id in enumerate(all_case_ids, start=1):
                embed.add_field(name=f'{i}:', value=case_id, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("You don't have necessary permissions to use this command.")


    @commands.command(help="Get all the list of cases against a specific user.")
    async def case_user(self, ctx, *, user: Union[discord.Member, discord.User]):
        if ctx.author.guild_permissions.manage_nicknames:
            self.load_case_ids()
            user_cases = [case_id for case_id, data in self.case_ids.items() if data["user_id"] == user.id]

            if user_cases:
                embed = discord.Embed(title=f"Cases for {user.display_name}", color=random_color)
                for i, case_id in enumerate(user_cases, start=1):
                    reason = self.case_ids[case_id]["reason"]
                    embed.add_field(name=f'Case {i}: {case_id}', value=f"Reason: {reason}", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No cases found for {user.display_name}.")
        else:
            await ctx.send("You don't have necessary permissions to use this command.")

    @commands.command(help="Removes a case against a specific user")
    async def remove_case(self, ctx, *, case_id: str):
        if ctx.author.guild_permissions.manage_nicknames:
            if case_id:
                if case_id in self.case_ids:
                    del self.case_ids[case_id]
                    self.save_case_ids()
                    await ctx.send(embed = discord.Embed(title="Success", description=f"Case has been removed.", color=random_color))
                else:
                    await ctx.send(embed = discord.Embed(title="Error", description=f"No such case found.", color=random_color))
            else:
                await ctx.send(embed = discord.Embed(title="Please provide a valid ID.", color=random_color))
        else:
            await ctx.send("You don't have necessary permissions to use this command.")



    @commands.command(name="kick", help="Kick a member")
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send(embed=discord.Embed(title="You don't have necessary permissions to use this command", color=random_color))
            return
        
        await member.kick(reason=reason)
        await ctx.send(embed=discord.Embed(title=f"{member.mention} has been kicked 👟"))

        # Log the action
        channel = discord.utils.get(ctx.guild.text_channels, name="oil-logs")
        if channel:
            embed = discord.Embed(title="Member Kicked",
                                description=f"{member.mention} has been kicked by {ctx.author.mention}",
                                color=discord.Color.red())
            embed.add_field(name="Reason", value=reason, inline=False)
            await channel.send(embed=embed)



async def setup(bot):
    await bot.add_cog(Moderation(bot))
