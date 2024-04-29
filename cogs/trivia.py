from discord.ext import commands
import requests
import discord
import asyncio

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="trivia", aliases = ["t", "quiz"],help="Get a trivia question")
    async def trivia(self, ctx):
        try:
            response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
            data = response.json()
            if response.status_code == 200 and data['response_code'] == 0:
                question = data['results'][0]['question']
                correct_answer = data['results'][0]['correct_answer']
                incorrect_answers = data['results'][0]['incorrect_answers']
                answers = incorrect_answers + [correct_answer]
                answers.sort()  # Shuffle the answers
                answers_text = "\n".join([f"{i+1}. {answer}" for i, answer in enumerate(answers)])

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

async def setup(bot):
    await bot.add_cog(Trivia(bot))