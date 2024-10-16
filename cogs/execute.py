import http.client
import base64
import re
from datetime import datetime
import discord
from discord.ext import commands
from discord import Embed, Color
from discord import app_commands
import json

# Your RapidAPI key for Judge0
JUDGE0_API_KEY = ''
JUDGE0_HOST = ''

class Execution(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.languages = []
        self.bot.loop.create_task(self.fetch_languages())  # Fetch languages on initialization

    async def fetch_languages(self):
        conn = http.client.HTTPSConnection(JUDGE0_HOST)
        headers = {
            'x-rapidapi-key': JUDGE0_API_KEY,
            'x-rapidapi-host': JUDGE0_HOST
        }
        try:
            conn.request("GET", "/languages/all", headers=headers)
            res = conn.getresponse()
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                self.languages = [(lang["name"], lang["id"]) for lang in data if not lang.get("is_archived")]
                print("Languages fetched:", self.languages)  # Log fetched languages
            else:
                print(f"Failed to fetch languages. Status code: {res.status}")
        except Exception as e:
            print(f"Error fetching languages: {e}")
        finally:
            conn.close()

    @app_commands.command(name="exec_languages")
    async def exec_languages(self, interaction: discord.Interaction):
        """Displays available languages for execution."""
        embed = discord.Embed(title="Languages available for execution", color=discord.Colour.blue())
        for lang in self.languages:
            embed.add_field(name=lang[0], value=str(lang[1]))
        await interaction.response.send_message(embed=embed)

    async def create_output_embed(self, token, stdout, stderr, compile_output, time, memory, language, description, author_name, author_icon):
        color = Color.green() if description == "Accepted" else Color.red()
        embed = Embed(colour=color, timestamp=datetime.utcnow())
        embed.set_author(name=f"{author_name}'s code execution", icon_url=author_icon)

        # Check if the output is base64 encoded before decoding
        stdout_decoded = self.decode_base64(stdout) if self.is_base64(stdout) else stdout
        stderr_decoded = self.decode_base64(stderr) if self.is_base64(stderr) else stderr
        compile_output_decoded = self.decode_base64(compile_output) if self.is_base64(compile_output) else compile_output

        output = self.concat_output(stdout_decoded, stderr_decoded, compile_output_decoded)
        embed = self.resize_output_for_embed(output, embed, token)

        if time:
            embed.add_field(name="Time", value=f"{time} s")
        if memory:
            embed.add_field(name="Memory", value=f"{round(memory / 1000, 2)} MB")
        embed.set_footer(text=f"{language} | {description}")

        return embed

    @staticmethod
    def is_base64(data):
        if not data:
            return False
        try:
            # Base64 strings must have a length multiple of 4 and only certain characters
            if len(data) % 4 == 0 and re.match(r'^[A-Za-z0-9+/=]+$', data):
                base64.b64decode(data.encode())
                return True
        except Exception:
            return False
        return False

    @staticmethod
    def decode_base64(data):
        try:
            return base64.b64decode(data.encode()).decode()
        except Exception:
            return f"[Error decoding output: Invalid base64]"

    @staticmethod
    def concat_output(stdout, stderr, compile_output):
        output = ""

        for each in (stdout, stderr, compile_output):
            if each:
                output += each + "\n"  # Append the output, keeping it simple

        return output if output else "No output"

    @staticmethod
    def resize_output_for_embed(output, embed, token):
        if len(output) > 300 or output.count("\n") > 10:
            embed.description = f"Output too large - [Full output](https://ide.link/{token})"
            output = "\n".join(output.split("\n")[:10]) + "\n(...)"
        embed.add_field(name="Output", value=f"```yaml\n{output}```", inline=False)
        return embed

    async def execute_code(self, interaction, lang_id, code):
        if code is None:
            await interaction.response.send_message("Please provide code to execute.")
            return

        await interaction.response.defer()
        await interaction.channel.send("⏳")  # Show a waiting message
        code = self.strip_source_code(code)
        submission = await self.get_submission(code, lang_id)

        if isinstance(submission, str):
            await interaction.response.send_message(submission)
            return

        await interaction.followup.send(embed=await self.create_output_embed(
            token=submission["token"],
            stdout=submission["stdout"],
            stderr=submission["stderr"],
            compile_output=submission["compile_output"],
            time=submission["time"],
            memory=submission["memory"],
            language=lang_id,
            description=submission["status"]["description"],
            author_name=str(interaction.user),
            author_icon=str(interaction.user.avatar.url) if interaction.user.avatar else str(interaction.user.default_avatar.url),
        ))

    @app_commands.command(name="exec", description="Execute source code.")
    @app_commands.describe(language="Select a programming language", code="Enter your code to execute.")
    async def exec_command(self, interaction: discord.Interaction, language: str, code: str):
        lang_id = int(language)  # Convert the string language ID to int
        await self.execute_code(interaction, lang_id, code)

    @exec_command.autocomplete("language")
    async def language_autocomplete(self, interaction: discord.Interaction, current: str):
        choices = [app_commands.Choice(name=lang[0], value=str(lang[1])) for lang in self.languages if current.lower() in lang[0].lower()]
        return choices[:25]  # Limit to 25 choices to avoid the 400 Bad Request error

    async def get_submission(self, source_code, language_id):
        conn = http.client.HTTPSConnection(JUDGE0_HOST)
        headers = {
            'x-rapidapi-key': JUDGE0_API_KEY,
            'x-rapidapi-host': JUDGE0_HOST,
            'Content-Type': "application/json"
        }

        payload = json.dumps({
            "source_code": base64.b64encode(source_code.encode()).decode(),
            "language_id": language_id
        })

        try:
            conn.request("POST", "/submissions?base64_encoded=true&wait=false", payload, headers)
            res = conn.getresponse()
            if res.status in [200, 201]:
                submission = json.loads(res.read().decode("utf-8"))
                return await self.wait_submission(submission["token"])  # Pass the token correctly
            else:
                return f"Error: {res.status} {res.reason}"
        except Exception as e:
            return f"Error submitting code: {e}"
        finally:
            conn.close()

    async def wait_submission(self, token):
        conn = http.client.HTTPSConnection(JUDGE0_HOST)
        headers = {
            'x-rapidapi-key': JUDGE0_API_KEY,
            'x-rapidapi-host': JUDGE0_HOST
        }

        while True:
            conn.request("GET", f"/submissions/{token}", headers=headers)
            res = conn.getresponse()
            if res.status in [200, 201]:
                data = json.loads(res.read().decode("utf-8"))
                if data["status"]["id"] not in [1, 2]:  # 1 = In Queue, 2 = Processing
                    return data
            else:
                return f"Error: {res.status} {res.reason}"

    @staticmethod
    def strip_source_code(code):
        code = code.strip("`")
        if re.match(r"\w*\n", code):
            code = "\n".join(code.split("\n")[1:])
        return code

    @app_commands.command(name="exec_languages")
    async def exec_languages(self, interaction: discord.Interaction):
        try:
            await interaction.user.send("https://ce.judge0.com/languages/all")
        except discord.Forbidden:
            await interaction.followup.send("Your DMs appear to be closed. I cannot send you the languages for execution.")

async def setup(bot):
    await bot.add_cog(Execution(bot))
