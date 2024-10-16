from discord.ext import commands
import discord
from discord import app_commands

class convertsion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="convert", aliases=["c"],  help="Convert stuff")
    async def convert(self, ctx, unit: str):
        try:
            value = float(unit[:-2])
            source_unit = unit[-2:]

            conversion_factors = {
                "kg" : {"kg": 1, "lb": 2.20462, "g": 1000, "oz": 35.274},
                "lb": {"kg": 0.453592, "lb": 1, "g": 453.592, "oz": 16},
                "mi": {"mi": 1, "km": 1.60934, "m": 1609.34, "yd": 1760, "ft": 5280, "in": 63360},
                "km": {"mi": 0.621371, "km": 1, "m": 1000, "yd": 1093.61, "ft": 3280.84, "in": 39370.1},
                "l": {"l": 1, "ga": 0.264172},
                "ga": {"l": 3.78541, "ga": 1}
            }

            results = {}
            for target_unit, factor in conversion_factors[source_unit].items():
                converted_value = value * factor
                results[target_unit] = converted_value

            embed = discord.Embed(title=f"Conversion of {value} {source_unit}", color=discord.Color.blue())
            for unit, converted_value in results.items():
                embed.add_field(name=unit, value=f"{converted_value:.2f}", inline=True)
            
            await ctx.send(embed=embed)

        except ValueError:
            await ctx.send("Invalid input. Please provide a valid unit. Note: No spaces between number and unit.")
            
    
    @app_commands.command(name="convert", description="Convert to and from stuff!")
    @app_commands.describe(unit = "What do you want to convert")
    async def convert_slash(self, interaction: discord.Interaction, unit: str):
        
        try:
            value = float(unit[:-2])
            source_unit = unit[-2:]

            conversion_factors = {
                "kg" : {"kg": 1, "lb": 2.20462, "g": 1000, "oz": 35.274},
                "lb": {"kg": 0.453592, "lb": 1, "g": 453.592, "oz": 16},
                "mi": {"mi": 1, "km": 1.60934, "m": 1609.34, "yd": 1760, "ft": 5280, "in": 63360},
                "km": {"mi": 0.621371, "km": 1, "m": 1000, "yd": 1093.61, "ft": 3280.84, "in": 39370.1},
                "l": {"l": 1, "ga": 0.264172},
                "ga": {"l": 3.78541, "ga": 1}
            }

            results = {}
            for target_unit, factor in conversion_factors[source_unit].items():
                converted_value = value * factor
                results[target_unit] = converted_value

            embed = discord.Embed(title=f"Conversion of {value} {source_unit}", color=discord.Color.blue())
            for unit, converted_value in results.items():
                embed.add_field(name=unit, value=f"{converted_value:.2f}", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message(embed = discord.Embed(title="Invalid input.", description=" Please provide a valid unit. Note: No spaces between number and unit.", color="FF0000"))
        
    
async def setup(bot):
    await bot.add_cog(convertsion(bot))
