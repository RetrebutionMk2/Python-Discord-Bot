from discord.ext import commands
import discord

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
    
async def setup(bot):
    await bot.add_cog(convertsion(bot))