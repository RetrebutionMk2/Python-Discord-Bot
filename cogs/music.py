import discord
import asyncio
import youtube_dl
import yt_dlp as youtube_dl
import glob
from discord.ext import commands
import os
import random
from discord import app_commands



intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True
bot = commands.Bot(command_prefix='$', intents=intents)

downloaded_files = []

youtube_dl.utils.bug_reports_message = lambda: ''
ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
    'preferredcodec': 'mp3'
}
ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)

        duration_seconds = data.get('duration')
        minutes, seconds = divmod(duration_seconds, 60)
        duration = f"`{minutes} min {seconds} sec`"
        thumbnail = data.get('thumbnail')
        return filename, duration, thumbnail
        


class Music(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.queue = asyncio.Queue()

    @commands.command(name='play', help='To play song')
    async def play(self, ctx, *, url):
        try:
            server = ctx.message.guild
            voice_channel = server.voice_client

            # Check if bot is connected to a voice channel
            if voice_channel is None:
                # If not connected, connect to the user's voice channel
                if ctx.author.voice:
                    voice_channel = await ctx.author.voice.channel.connect()
                else:
                    await ctx.send("Please join a voice channel first.")
                    return

            # Add the URL to the queue
            await self.queue.put(url)

            # Check if the bot is already playing something
            if not voice_channel.is_playing():
                # If not playing, play the next song in the queue
                await self.play_next(ctx)
            else:
                queue_list = [url for url in self.queue._queue]
                if queue_list:
                    # Create an embed to display the queue
                    embed = discord.Embed(title='Song added to queue!', color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                    for i, url in enumerate(queue_list, start=1):
                        embed.add_field(name=f'Song {i}:', value=url, inline=False)
                    await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred while playing the song: {e}")


    @commands.command(name='next', help='To skip/play next song')
    async def play_next(self, ctx):
        try:
            voice_channel = ctx.message.guild.voice_client

            if not self.queue.empty():
                url = await self.queue.get()
                async with ctx.typing():
                    filename, duration, thumbnail = await YTDLSource.from_url(url, loop=self.bot.loop)
                    source = discord.FFmpegPCMAudio(filename, executable="ffmpeg.exe")
                    voice_channel.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
                    
                # Remove file extension from filename
                filename_without_extension = os.path.splitext(os.path.basename(filename))[0]
                proper_filename = filename_without_extension.split('_')
                proper_filename = ' '.join(str(x) for x in proper_filename)
                embed = discord.Embed(title='Now playing', description=f'**Title:** {proper_filename[:-14]}\n**Requested by:** {ctx.author}', color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                embed.add_field(name="Duration", value=duration)
                embed.add_field(name="Queue", value=f"`{self.queue.qsize()}`")
                embed.set_thumbnail(url=thumbnail)
                await ctx.send(embed=embed)

                # Delete downloaded files after each song
                try:
                    for file in glob.glob("*.webm"):
                        os.remove(file)
                except Exception as e:
                    print(f"An error occurred while deleting the cache: {e}")

            else:
                await ctx.send(embed=discord.Embed(title=None, description="Attempting to play next song.", color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))))
        except Exception as e:
            print(f"An error occurred while playing the next song: {e}")



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user and before.channel and not after.channel:
            # Bot left the voice channel
            if before.channel.guild.voice_client:
                # Check if there are more songs in the queue
                if not self.queue.empty():
                    # Play the next song in the queue
                    await self.play_next(before.channel.guild.voice_client)
                else:
                    # Queue is empty, leave the voice channel
                    await before.channel.guild.voice_client.disconnect()


    @commands.command(name='queue', help='To view the current queue')
    async def show_queue(self, ctx):
        try:
            # Get the URLs of songs in the queue
            queue_list = [url for url in self.queue._queue]
            if queue_list:
                # Create an embed to display the queue
                embed = discord.Embed(title='Current Queue', color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
                for i, url in enumerate(queue_list, start=1):
                    embed.add_field(name=f'Song {i}:', value=url, inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("The queue is empty.")
        except Exception as e:
            await ctx.send(f"An error occurred while viewing the queue: {e}")

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            embed = discord.Embed(title='Paused', description='The song has been paused.', color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            await ctx.send(embed=embed)
        elif voice_client and voice_client.is_paused():
            await ctx.send("The song is already paused.")
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            embed = discord.Embed(title='Resumed', description='The song has been resumed.', color=discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            await ctx.send(embed=embed)
        elif voice_client and voice_client.is_playing():
            await ctx.send("The song is already playing.")
        else:
            await ctx.send("The bot was not playing anything before this. Use the play command.")

    @commands.command(name='skip', help='To skip the current song')
    async def skip(self, ctx):
        try:
            voice_channel = ctx.message.guild.voice_client

            if not voice_channel or not voice_channel.is_playing():
                await ctx.send("There's no song currently playing.")
                return

            # Stop the currently playing song
            voice_channel.stop()

            # Check if there are more songs in the queue
            if not self.queue.empty():
                # Play the next song in the queue
                await self.play_next(ctx)
            else:
                # No more songs in the queue, stop playback
                await ctx.send("No more songs in the queue.")

        except Exception as e:
            await ctx.send(f"An error occurred while skipping the current song: {e}")

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            embed = discord.Embed(title='Stopped', description='The song has been stopped.', color=discord.Color.red())
            await ctx.send(embed=embed)
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name='remove', help='To remove a song from the queue')
    async def remove(self, ctx, index: int):
        try:
            # Check if the index is valid
            if index < 1 or index > self.queue.qsize():
                await ctx.send("Invalid index. Please provide a valid index.")
                return

            # Remove the song at the specified index from the queue
            removed_url = await self.remove_from_queue(index)

            if removed_url:
                await ctx.send(f"Song at index {index} has been removed from the queue.")
            else:
                await ctx.send("Failed to remove song from the queue.")
        except Exception as e:
            await ctx.send(f"An error occurred while removing the song: {e}")

    async def remove_from_queue(self, index):
        try:
            # Initialize an empty list to store the removed items
            removed_items = []

            # Remove items from the queue until the specified index
            for _ in range(index - 1):
                item = await self.queue.get()
                removed_items.append(item)

            # Remove the item at the specified index
            removed_url = await self.queue.get()

            # Add back the removed items to the queue
            for item in removed_items:
                await self.queue.put(item)

            return removed_url
        except Exception as e:
            print(f"An error occurred while removing from queue: {e}")
            return None
        
    @commands.command(name='join', help="Make the bot join the vc")
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("You are not connected to a voice channel.")
            return

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.voice_client

        if voice_client is None:
            voice_client = await voice_channel.connect()
            # Delete downloaded files after each song
            try:
                for file in glob.glob("*.webm"):
                    os.remove(file)
            except Exception as e:
                print(f"An error occurred while deleting the cache: {e}")
            
            try:
                for file in glob.glob("*.m4a"):
                    os.remove(file)
            except Exception as e:
                print(f"An error occurred while deleting the cache: {e}")

        else:
            if voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)

    @commands.command(name='leave', help="Tell the bot to leave the vc")
    async def leave(self, ctx):
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
            await ctx.send('Bot left')
            # Delete downloaded files after each song
            try:
                for file in glob.glob("*.webm"):
                    os.remove(file)
            except Exception as e:
                print(f"An error occurred while deleting the cache: {e}")
            await ctx.send('Cache cleared')
        else:
            await ctx.send("I'm not in a voice channel, use the join command to make me join")


async def setup(bot):
    await bot.add_cog(Music(bot))
