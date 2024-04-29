import os
import discord
from discord.ext import commands
from googlesearch import search as find
import asyncio
import tracemalloc
import random
import string
from badwords import get_badwords_data
from auto_mod import add_auto_mod_server
from auto_mod import is_auto_mod_active
from auto_mod import remove_auto_mod_server

tracemalloc.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True
downloaded_files = []
queue = asyncio.Queue()
DEFAULT_COLOR = 0x000000

bot = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='$', intents=intents)

global random_color
random_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


@bot.event
async def on_ready():
    print('We have logged in as {0}'.format(bot))
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('Watching over you\n Prefix: $'))
    await load_extensions()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    server_id = message.guild.id
    badwords_data = await get_badwords_data()
    badwords = badwords_data["bad_words"]
    
    if await is_auto_mod_active(server_id):
        message_content_cleaned = ''.join(char  for char in message.content if char not in string.punctuation)
        words = message_content_cleaned.split()

        for word in words:
            if word in badwords:
                await message.delete()
                bad_word_embed = discord.Embed(title=f"{message.author}, Hey! That word is not allowed here!", color=random_color)
                await message.channel.send(embed=bad_word_embed)
                break
        
    if bot.user.mentioned_in(message):
        if 'retrebutionmk2' in message.content.lower():
            await message.channel.send(embed=discord.Embed(title='Hey there! You contacted the Server Admin. He might be busy but in time you can create a ticket in #support.', color=random_color))

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    guild = member.guild
    role_name = "Awaiting Verify"

    role = discord.utils.get(member.guild.roles, name=role_name)

    if role is None:
        role = await guild.create_role(name=role_name)

        permissions = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(guild.channels, name='·》︱support'): discord.PermissionOverwrite(read_messages=True)
        }

        for channel in guild.channels:
            await channel.set_permissions(role, overwrite=permissions.get(channel, discord.PermissionOverwrite()))
    
    await member.add_roles(role)

    image_url = "https://c.tenor.com/qV9QZcasa-QAAAAd/welcome.gif"
    embed = discord.Embed(
        title=f"Welcome {member.name}!",
        description=f"Welcome to the server! You have been granted access to the support channel.",
        color=discord.Color.green()
    )
    # Access avatar URL using member.avatar.url
    embed.set_thumbnail(url=member.avatar.url)  # Set member's avatar as thumbnail
    embed.set_image(url=image_url)  # Set the image URL passed as argument


    # Get the support channel
    welcome_channel = discord.utils.get(member.guild.channels, name='·》︱new-members')
    
    # Send the embed to the support channel
    await welcome_channel.send(embed=embed)


@bot.command(name="automod", help="Enables automod for the server")
@commands.has_permissions(administrator=True)
async def automod_enable(ctx):
    await add_auto_mod_server(ctx.guild.id)
    await ctx.send(embed=discord.Embed(title="Automod", description="Auto mod has been enabled for this server!!!", color=random_color))

@bot.command(name='removeautomod', help="Removes automod from the server")
@commands.has_permissions(administrator=True)
async def remove_auto_mod(ctx):
    await remove_auto_mod_server(ctx.guild.id)
    await ctx.send("Auto moderation disabled for this server.")


@bot.command(name='search', help="search up the wiki")
async def search(ctx, *, query):
    search_query = f'{query} -filetype:png -filetype:jpg -filetype:jpeg -filetype:gif -filetype:bmp site: google.com'

    try:
        # Perform a Google search
        results = list(find(search_query, num=1, stop=1, pause=2))
        if results:
            await ctx.send(f"Here's what I found:\n {results[0]}")
        else:
            await ctx.send("Sorry, I couldn't find any information. Did you want to search outside of wikipedia? Make sure your search query is as if you are searching on wikipedia and not google")
    except Exception as e:
        print(e)
        await ctx.send("An error occurred while searching.")



@bot.command(name='invite', help="Invite the bot")
async def invite(ctx):
    await ctx.send('https://discord.com/api/oauth2/authorize?client_id=875228716698058802&permissions=8&scope=bot')


@bot.command(help="Say something using the bot. Format: $say [text channel] [text]")
async def say(ctx, channel: discord.TextChannel, *, message: str):
    if channel.permissions_for(ctx.author).send_messages:
        try:
            await channel.send(message)
            await ctx.send(f"Message sent to {channel.mention}")
        except discord.Forbidden:
            await ctx.send("Could not send the message. Check if the bot has permissions to send messages in that channel.")
    else:
        await ctx.send("You don't have permissions to use this command.")


'''
@bot.command(name='rule')
async def rule(ctx):
    rules = "Respect Others: Treat all members with kindness and respect. Harassment, hate speech, discrimination, and personal attacks will not be tolerated.\n\n No Spamming or Flooding: Avoid sending repeated messages, excessive emojis, or posting irrelevant content. Keep conversations constructive and on-topic.\n\nNo NSFW Content: Do not share or discuss any explicit or inappropriate content, including images, videos, or links. This is a safe space for all ages.\n\nNo Advertising or Self-Promotion: Refrain from promoting personal projects, social media accounts, or external communities without permission from the moderators.\n\nUse Appropriate Channels: Post content in the relevant channels to keep discussions organized. Off-topic conversations should be moved to appropriate channels or kept to a minimum.\n\nNo Spoilers: Respect others' enjoyment by refraining from posting spoilers without proper warning and spoiler tags. Use spoiler tags when discussing sensitive content.\n\nFollow Discord Terms of Service: Abide by Discord's community guidelines and terms of service at all times. Any violations may result in disciplinary action.\n\nListen to Moderators: Follow instructions given by moderators and administrators. They are here to ensure a positive and enjoyable experience for everyone.\n\nKeep Conversations Civil: Engage in constructive dialogue and avoid heated arguments or debates. Disagreements are fine, but keep discussions civil and respectful.\n\nNo Unauthorized Bots: Do not add bots to the server without permission from the administrators. Unauthorized bots may be removed without notice.\n\nNo Impersonation: Do not impersonate other members, moderators, or administrators. This includes using similar usernames or profile pictures.\n\nRespect Privacy: Do not share personal information about yourself or others without consent. Protect your privacy and the privacy of others.\n\nNo free ranking: Do not give roles to other eole and do not give ranks to yourself.\n\nNo bypassing the automod: do not try to bypass the automod using emojis or anything else.\n\nNo deleting roles from yourself.\n\nRules can and will be changed as needed.\n\nThere are a few things that are not in the rules but its common sense to not break them."

    embed = discord.Embed(title="Rules", description=rules)
    embed.set_image(url="https://panels.twitch.tv/panel-409370050-image-ac70e06d-a6c4-4e11-bf95-2b0f174f9db4")
    embed.set_thumbnail(url="https://panels.twitch.tv/panel-409370050-image-ac70e06d-a6c4-4e11-bf95-2b0f174f9db4")

    await ctx.send(embed=embed)
'''

try:
  token = ''
  if token == "":
      raise Exception("Please add your token to the Secrets pane.")
  bot.run(token)
except discord.HTTPException as e:
  if e.status == 429:
      print(
          "The Discord servers denied the connection for making too many requests"
      )
      print(
          "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
      )
  else:
      raise e
