from discord.ext import commands
import requests
import discord
import random

class dog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    global random_color
    random_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    @commands.command(name="dog", help="Find a cute dog")
    async def dog(self, ctx):
        #thecatapi -> live_GNVdli4mxxi0NcRMLGhEAmJCM5a9KvOlGZwXAKZCEiuqjTZpeX3D2BSm33j2iKgG
        response = requests.get('https://api.thedogapi.com/v1/images/search?limit=1')
        data = response.json()
        dog_image_url = data[0]['url']
        embed = discord.Embed(title="🐶Woof...", color=random_color, url=dog_image_url)
        embed.set_image(url=dog_image_url)

        await ctx.send(embed=embed)

    @commands.command(name="cat", help="Find a cute cat")
    async def cat(self, ctx):
        #thecatapi -> live_GNVdli4mxxi0NcRMLGhEAmJCM5a9KvOlGZwXAKZCEiuqjTZpeX3D2BSm33j2iKgG
        response = requests.get('https://api.thecatapi.com/v1/images/search?limit=1')
        data = response.json()
        cat_image_url = data[0]['url']
        embed = discord.Embed(title="🐱Meow...", color=random_color, url=cat_image_url)
        embed.set_image(url=cat_image_url)

        await ctx.send(embed=embed)

    @commands.command(name="fox", help="Find a cute fox")
    async def fox(self, ctx):
        response = requests.get('https://randomfox.ca/floof/')
        data = response.json()
        fox_image_url = data["image"]
        fox_image_link = data["link"]

        embed = discord.Embed(title="🦊Foxxy...", color=discord.Color.random(), url=fox_image_link)
        embed.set_image(url=fox_image_url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(dog(bot))