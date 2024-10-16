from discord.ext import commands
import requests
import discord
from discord import app_commands

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.calls_made = 0


    def get_weather(self, city):
        try:
            if self.calls_made >=999000:
                raise Exception("API call limit exceeded.")

            base_url = "" # <-- this is the api key to www.weatherapi.com
            complete_url = base_url + "&q=" + city
            response =  requests.get(complete_url) 
            result = response.json()

            self.calls_made += 1

            city = result['location']['name']
            country = result['location']['country']
            time = result['location']['localtime']
            wcond = result['current']['condition']['text']
            celcius = result['current']['temp_c']
            fahrenheit = result['current']['temp_f']
            fclike = result['current']['feelslike_c']
            fflike = result['current']['feelslike_f']
            wind_mph = result['current']['wind_mph']
            wind_kph = result['current']['wind_kph']
            humidity = result['current']['humidity']


            embed=discord.Embed(title=f"{city}"' Weather', description=f"{country}", color=0x14aaeb)
            embed.add_field(name="Temprature C°", value=f"{celcius}", inline=True)
            embed.add_field(name="Temprature F°", value=f"{fahrenheit}", inline=True)
            embed.add_field(name="Wind Condition", value=f"{wcond}", inline=False)
            embed.add_field(name="Feels Like F°", value=f"{fflike}", inline=True)
            embed.add_field(name="Feels Like C°", value=f"{fclike}", inline=True)
            embed.add_field(name="Humidity", value=f"{humidity}", inline=False)
            embed.add_field(name="Wind mph", value=f"{wind_mph}", inline=True)
            embed.add_field(name="Wind kph", value=f"{wind_kph}", inline=True)
            embed.set_footer(text='Time: 'f"{time}")

            return embed
        except Exception as e:
            print(e)
            embed=discord.Embed(title="No response", color=0x14aaeb)
            embed.add_field(name="Error", value="Oops!! Please enter a city name", inline=True)
            return embed
        
    @commands.command(name="weather", help="Provides you with weather info.")
    async def weather(self, ctx, *, city):
        embed = self.get_weather(city)
        await ctx.send(embed=embed)

    @app_commands.command(name="weather", description="How's the weather?")
    @app_commands.describe(city = "Name of the city/state")
    async def weather_slash(self, interaction: discord.Interaction, city: str):
        embed = self.get_weather(city)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Weather(bot))
