from discord.ext import commands
import discord
from discord import app_commands
from googleapiclient.discovery import build

class search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="search", description="Search up the wiki")
    @app_commands.describe(query="What to search up", numberofresults = "Number of results (1-5)", dm = "Yes or No. If you want the results to be DM'd or not")
    @app_commands.choices(dm = [
        app_commands.Choice(name="Yes", value="yes"),
        app_commands.Choice(name="No", value="no")
        ])
    async def search_slash(self, interaction: discord.Interaction, *, query: str, numberofresults: int, dm: str):

        await interaction.response.defer()
        
        if numberofresults >6:
            await interaction.followup.send("Please enter less than 6 responses only.")
            return

        # Set up Google API
        api_key = ''  # Custom search api
        cx = ''  # Custom Search Engine ID

        # Build the service
        service = build("customsearch", "v1", developerKey=api_key)

        # Perform the search
        result = service.cse().list(q=query, cx=cx, num=numberofresults).execute()  # Fetch top 5 results
        urls = [item['link'] for item in result.get('items', [])]

        if not urls:
            await interaction.followup.send("No results found")
            return
        
        if dm == "yes":
            try:
                for url in urls:
                    await interaction.user.send(f"{url}")
                await interaction.followup.send("Sent the results to your DMs!")
            except discord.Forbidden:
                await interaction.followup.send("Unable to send DMs. Please check your settings.")

        if dm == "no":
            for url in urls:
                await interaction.followup.send(f"{url}")

async def setup(bot):
    await bot.add_cog(search(bot))
