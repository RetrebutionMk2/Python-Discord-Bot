from discord.ext import commands
import requests
import discord
import asyncio
from discord import app_commands
from discord.ui import Button, View
import html

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="trivia", aliases=["t", "quiz"], help="Get a trivia question")
    async def trivia(self, ctx):
        try:
            response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
            data = response.json()
            if response.status_code == 200 and data['response_code'] == 0:
                question = html.unescape(data['results'][0]['question'])
                correct_answer = html.unescape(data['results'][0]['correct_answer'])
                incorrect_answers = [html.unescape(answer) for answer in data['results'][0]['incorrect_answers']]
                answers = incorrect_answers + [correct_answer]
                answers.sort()
                answers_text = "\n".join([f"{i + 1}. {answer}" for i, answer in enumerate(answers)])

                embed = discord.Embed(title="Trivia Question", description=question, color=discord.Color.blue())
                embed.add_field(name="Options", value=answers_text, inline=False)
                await ctx.send(embed=embed)

                def check_answer(m):
                    return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

                try:
                    user_response = await self.bot.wait_for('message', timeout=30.0, check=check_answer)
                    selected_answer = int(user_response.content)
                    if 1 <= selected_answer <= len(answers):
                        if answers[selected_answer - 1] == correct_answer:
                            await ctx.send("Correct answer!")
                        else:
                            await ctx.send(f"Sorry, the correct answer was: {correct_answer}")
                    else:
                        await ctx.send("Invalid choice. Please select a number corresponding to one of the options.")
                except asyncio.TimeoutError:
                    await ctx.send("You took too long to respond.")

            else:
                await ctx.send("Failed to fetch trivia question.")

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @app_commands.command(name="trivia", description="Answer some challenging questions")
    async def trivia_slash(self, interaction: discord.Interaction):
        try:
            response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
            data = response.json()
            if response.status_code == 200 and data['response_code'] == 0:
                question = html.unescape(data['results'][0]['question'])
                correct_answer = html.unescape(data['results'][0]['correct_answer'])
                incorrect_answers = [html.unescape(answer) for answer in data['results'][0]['incorrect_answers']]
                answers = incorrect_answers + [correct_answer]
                answers.sort()

                buttons = {i + 1: Button(label=str(i + 1), custom_id=str(i + 1), style=discord.ButtonStyle.primary) for i in range(len(answers))}
                options_text = "\n".join([f"{i + 1}. {answer}" for i, answer in enumerate(answers)])
                embed = discord.Embed(
                    title="Trivia Question",
                    description=f"**Question:** {question}\n\n**Options:**\n{options_text} \n\n 30s to answer",
                    color=discord.Color.blue()
                )

                class TriviaView(View):
                    def __init__(self, timeout):
                        super().__init__(timeout=timeout)
                        self.correct_answer = correct_answer
                        self.stop_event = asyncio.Event()
                        self.task = None
                        for button in buttons.values():
                            button.callback = self.button_callback
                            self.add_item(button)

                    async def button_callback(self, interaction: discord.Interaction):
                        if self.stop_event.is_set():
                            await interaction.response.send_message("❗ The trivia has already ended.")
                            return

                        selected_answer = int(interaction.data['custom_id'])
                        if answers[selected_answer - 1] == self.correct_answer:
                            await interaction.response.send_message("✅ Correct answer!")
                        else:
                            await interaction.response.send_message(f"❌ Sorry, the correct answer was: {self.correct_answer}")

                        # Disable all buttons after an answer is selected
                        for item in self.children:
                            item.disabled = True
                        await interaction.message.edit(view=self)
                        self.stop_event.set()  # Signal that the trivia is over

                        # Cancel the timeout task
                        if self.task:
                            self.task.cancel()

                    async def wait_for_timeout(self):
                        try:
                            await asyncio.wait_for(self.stop_event.wait(), timeout=30.0)
                        except asyncio.TimeoutError:
                            for item in self.children:
                                item.disabled = True
                            await self.message.edit(view=self)
                            await self.message.channel.send(f"⏰ Time's up! The correct answer was: {self.correct_answer}")
                        except asyncio.CancelledError:
                            pass

                view = TriviaView(timeout=30.0)
                message = await interaction.response.send_message(embed=embed, view=view)
                view.message = message

                # Start the timeout waiting in the background
                view.task = self.bot.loop.create_task(view.wait_for_timeout())

            else:
                await interaction.response.send_message("⚠️ Failed to fetch trivia question.")

        except Exception as e:
            await interaction.response.send_message(f"❗ An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Trivia(bot))