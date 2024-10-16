from discord.ext import commands
from discord import app_commands
import discord
import asyncio
import random
import json
from typing import Union
from typing import Optional
from datetime import datetime, timedelta

CASE_FILE_PATH = "./cogs/case_ids.json"

class ModerationSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_case_ids()
        self.random_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def load_case_ids(self):
        try:
            with open(CASE_FILE_PATH, "r") as file:
                self.case_ids = json.load(file)
        except FileNotFoundError:
            self.case_ids = {}
        except json.JSONDecodeError:
            self.case_ids = {}

        for case_id, data in self.case_ids.items():
            data["user_id"] = int(data["user_id"])

    def save_case_ids(self):
        with open(CASE_FILE_PATH, "w") as file:
            json.dump({case_id: {"user_id": int(data["user_id"]), "reason": data["reason"]} for case_id, data in self.case_ids.items()}, file, indent=4)

    @app_commands.command(name="purge", description="Bulk delete messages")
    @app_commands.describe(amount="Number of messages to delete")
    @app_commands.default_permissions(manage_messages=True)
    async def purge_slash(self, interaction: discord.Interaction, amount: int):
        if interaction.user.guild_permissions.manage_messages:
            try:
                # Defer the interaction without sending any message to the user (acknowledges the interaction)
                await interaction.response.defer(thinking=False)  # Silent deferral

                # Purge the messages
                deleted_messages = await interaction.channel.purge(limit=amount+1)
                deleted_count = len(deleted_messages)  # Actual number of deleted messages

                # Send the response message to the channel
                embed1 = discord.Embed(title="Purge", description=f"{deleted_count} messages deleted.", color=discord.Color.blue())
                await interaction.channel.send(embed=embed1)

                # Log the purge action
                log_channel = discord.utils.get(interaction.guild.text_channels, name="oil-logs")
                if log_channel:
                    embed2 = discord.Embed(title="Purge command used",
                                        description=f"Purge command used by {interaction.user.mention}",
                                        color=discord.Color.red())
                    embed2.add_field(name="Amount", value=deleted_count, inline=False)
                    await log_channel.send(embed=embed2)

            except discord.Forbidden:
                await interaction.channel.send("I don't have permissions to delete messages.")
            except discord.NotFound:
                await interaction.channel.send("An error occurred: Messages or the channel couldn't be found.")
            except discord.HTTPException as e:
                await interaction.channel.send(f"An unexpected error occurred: {str(e)}")
        else:
            await interaction.channel.send("You don't have permission to use this command.")


    @app_commands.command(name="timeout", description="Timeout a member")
    @app_commands.describe(member="Member to timeout", duration="Duration in minutes")
    @app_commands.default_permissions(manage_nicknames=True)
    async def timeout_slash(self, interaction: discord.Interaction, member: discord.Member, duration: int):
        if duration <= 0:
            await interaction.response.send_message("Duration must be greater than 0 minutes.")
            return

        # Ensure bot has the right permissions and role hierarchy
        if interaction.user.top_role <= member.top_role:
            await interaction.response.send_message("You cannot timeout a member with an equal or higher role.")
            return

        timeout_end = datetime.utcnow() + timedelta(minutes=duration)  # Calculate end time

        # Optionally, set a max timeout duration
        max_timeout = 24 * 60  # 24 hours in minutes
        if duration > max_timeout:
            await interaction.response.send_message(f"Duration cannot exceed {max_timeout} minutes.")
            return
        
        try:
            await member.timeout(timeout_end)
            await interaction.response.send_message(embed=discord.Embed(title="Timeout", description=f"{member.mention} has been timed out for {duration} minute(s).", color=self.random_color))
            
            # Log the action
            log_channel = discord.utils.get(interaction.guild.text_channels, name="oil-logs")
            if log_channel:
                embed = discord.Embed(title="Member Timed Out",
                                    description=f"{member.mention} has been timed out by {interaction.user.mention} for {duration} minute(s).",
                                    color=discord.Color.red())
                await log_channel.send(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("I don't have the necessary permissions to timeout this member.")
        except discord.HTTPException as e:
            await interaction.response.send_message(f"An error occurred: {e}")

    @app_commands.command(name="mute", description="Mute a member")
    @app_commands.describe(member="Member to mute", duration="Duration in minutes")
    @app_commands.default_permissions(manage_roles=True)
    async def mute_slash(self, interaction: discord.Interaction, member: discord.Member, duration: int):
        if duration <= 0:
            await interaction.response.send_message("Duration must be greater than 0 minutes.")
            return

        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="Muted")

            for channel in interaction.guild.text_channels:
                await channel.set_permissions(muted_role, send_messages=False)

        appeals_channel = discord.utils.get(interaction.guild.channels, name="appeals")
        if appeals_channel:
            await appeals_channel.set_permissions(muted_role, send_messages=True)

        await member.add_roles(muted_role)
        await interaction.response.send_message(embed=discord.Embed(title="Mute", description=f"{member.mention} has been muted for {duration} minutes.", color=self.random_color))

        log_channel = discord.utils.get(interaction.guild.text_channels, name="oil-logs")
        if log_channel:
            embed = discord.Embed(title="Member Muted",
                                description=f"{member.mention} has been muted by {interaction.user.mention}",
                                color=discord.Color.red())
            await log_channel.send(embed=embed)

        await asyncio.sleep(duration * 60)
        
        await member.remove_roles(muted_role)
        await interaction.followup.send(f"{member.mention} has been unmuted.")

    @app_commands.command(name="unmute", description="Unmute a member")
    @app_commands.describe(member="Member to unmute")
    @app_commands.default_permissions(manage_roles=True)
    async def unmute_slash(self, interaction: discord.Interaction, member: discord.Member):
        if interaction.user.guild_permissions.manage_roles:
            muted_role = discord.utils.get(interaction.guild.roles, name="Muted")
            if muted_role:
                try:
                    await member.remove_roles(muted_role, reason="Unmuted")
                    await interaction.response.send_message(f"{member.mention} has been unmuted.")
                except discord.Forbidden:
                    await interaction.response.send_message("I don't have the necessary permissions to manage roles.")
            else:
                await interaction.response.send_message("Muted role not found.")
        else:
            await interaction.response.send_message("You don't have the necessary permissions to use this command.")

    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.describe(member="Member to ban", reason="Reason for ban")
    @app_commands.default_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, *, reason: Optional[str] = None):
        if interaction.user.guild_permissions.ban_members:
            try:
                await member.ban(reason=reason)
                await interaction.response.send_message(embed=discord.Embed(title="BAN", description=f"**{member.mention} has been banned.**", color=self.random_color))
                
                log_channel = discord.utils.get(interaction.guild.text_channels, name="oil-logs")
                if log_channel:
                    embed = discord.Embed(title="Member Banned",
                                        description=f"{member.mention} has been banned by {interaction.user.mention}",
                                        color=discord.Color.red())
                    embed.add_field(name="Reason", value=reason, inline=False)
                    await log_channel.send(embed=embed)
                
            except discord.Forbidden:
                await interaction.response.send_message("I don't have the necessary permissions to ban members.")
        else:
            await interaction.response.send_message("You don't have the necessary permissions to use this command.")

    @app_commands.command(name="unban", description="Unban a member")
    @app_commands.describe(userid="User ID to unban", reason="Reason for unban")
    @app_commands.default_permissions(ban_members=True)
    async def unban_slash(self, interaction: discord.Interaction, userid: int, *, reason: Optional[str] = None):
        if interaction.user.guild_permissions.ban_members:
            try:
                await interaction.guild.unban(user=discord.Object(id=userid), reason=reason)
                await interaction.response.send_message("User unbanned.")
            except discord.Forbidden:
                await interaction.response.send_message("I don't have the necessary permissions to unban members.")
        else:
            await interaction.response.send_message("You don't have the necessary permissions to use this command.")

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason for the warning")
    @app_commands.default_permissions(manage_roles=True)
    async def warn_slash(self, interaction: discord.Interaction, member: discord.Member, *, reason: Optional[str] = None):
        if interaction.user.guild_permissions.manage_roles:
            case_id = self.generate_case_id()
            self.case_ids[case_id] = {"user_id": member.id, "reason": reason}
            self.save_case_ids()
            embed = discord.Embed(title='Warn', description=f'{member.display_name} has been warned.\n Reason: {reason} \n Case id = {case_id}', color=self.random_color)
            try:
                await member.send(embed=embed)
                await interaction.response.send_message(embed=embed)
            except discord.Forbidden:
                await interaction.response.send_message("I don't have necessary permissions to warn members.")
        else:
            await interaction.response.send_message("You don't have necessary permissions to use this command.")

        log_channel = discord.utils.get(interaction.guild.text_channels, name="oil-logs")
        if log_channel:
            embed = discord.Embed(title="Member Warned",
                                description=f"{member.mention} has been warned by {interaction.user.mention}",
                                color=discord.Color.red())
            embed.add_field(name="Reason", value=reason, inline=False)
            await log_channel.send(embed=embed)
            
    def generate_case_id(self):
        while True:
            case_id = ''.join(random.choices('0123456789', k=5))
            if not case_id in self.case_ids:
                return case_id

    @app_commands.command(name="case", description="Retrieve details of a specific case")
    @app_commands.describe(case_id="ID of the case to retrieve")
    @app_commands.default_permissions(manage_nicknames=True)
    async def case_slash(self, interaction: discord.Interaction, case_id: str):
        if interaction.user.guild_permissions.manage_nicknames:
            self.load_case_ids()
            if case_id in self.case_ids:
                member_id, reason = self.case_ids[case_id]["user_id"], self.case_ids[case_id]["reason"]
                member = interaction.guild.get_member(member_id)
                embed = discord.Embed(title=f"Case {case_id}", description=f"Member: {member.display_name if member else 'Unknown'} \n Reason: {reason if reason else 'No reason provided'}", color=self.random_color)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(embed=discord.Embed(title=f"Case {case_id}", description="Case not found", color=self.random_color))
        else:
            await interaction.response.send_message("You don't have necessary permissions to use this command.")

    @app_commands.command(name="server_cases", description="Get all the list of cases in the server.")
    @app_commands.default_permissions(manage_nicknames=True)
    async def server_cases_slash(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_nicknames:
            self.load_case_ids()
            all_case_ids = self.case_ids
            embed = discord.Embed(title="Case IDs", color=self.random_color)
            for i, case_id in enumerate(all_case_ids, start=1):
                embed.add_field(name=f'{i}:', value=case_id, inline=False)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("You don't have necessary permissions to use this command.")

    @app_commands.command(name="case_user", description="Get all the list of cases against a specific user.")
    @app_commands.describe(user="User to get cases for")
    @app_commands.default_permissions(manage_nicknames=True)
    async def case_user_slash(self, interaction: discord.Interaction, user: Union[discord.Member, discord.User]):
        if interaction.user.guild_permissions.manage_nicknames:
            self.load_case_ids()
            user_cases = [case_id for case_id, data in self.case_ids.items() if data["user_id"] == user.id]

            if user_cases:
                embed = discord.Embed(title=f"Cases for {user.display_name}", color=self.random_color)
                for i, case_id in enumerate(user_cases, start=1):
                    reason = self.case_ids[case_id]["reason"]
                    embed.add_field(name=f'Case {i}: {case_id}', value=f"Reason: {reason}", inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"No cases found for {user.display_name}.")
        else:
            await interaction.response.send_message("You don't have necessary permissions to use this command.")

    @app_commands.command(name="remove_case", description="Removes a case against a specific user")
    @app_commands.describe(case_id="ID of the case to remove")
    @app_commands.default_permissions(manage_nicknames=True)
    async def remove_case_slash(self, interaction: discord.Interaction, case_id: str):
        if interaction.user.guild_permissions.manage_nicknames:
            if case_id:
                if case_id in self.case_ids:
                    del self.case_ids[case_id]
                    self.save_case_ids()
                    await interaction.response.send_message(embed=discord.Embed(title="Success", description="Case has been removed.", color=self.random_color))
                else:
                    await interaction.response.send_message(embed=discord.Embed(title="Error", description="No such case found.", color=self.random_color))
            else:
                await interaction.response.send_message(embed=discord.Embed(title="Please provide a valid ID.", color=self.random_color))
        else:
            await interaction.response.send_message("You don't have necessary permissions to use this command.")

    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.describe(member="Member to kick", reason="Reason for kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, *, reason: Optional[str] = None):
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(embed=discord.Embed(title="You don't have necessary permissions to use this command", color=self.random_color))
            return
        
        await member.kick(reason=reason)
        await interaction.response.send_message(embed=discord.Embed(title=f"{member.mention} has been kicked 👟"))

        log_channel = discord.utils.get(interaction.guild.text_channels, name="oil-logs")
        if log_channel:
            embed = discord.Embed(title="Member Kicked",
                                description=f"{member.mention} has been kicked by {interaction.user.mention}",
                                color=discord.Color.red())
            embed.add_field(name="Reason", value=reason, inline=False)
            await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ModerationSlash(bot))
