# import packages
import asyncio
import discord
import html2text
import youtube_dl
from discord.ext import commands, tasks
from gtts import gTTS
import configparser

from faapi import check_notif, reload_data, random_submission


config = configparser.ConfigParser()
config.read('config.ini')
bot_config = config['bot']

h = html2text.HTML2Text()

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
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
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class FAChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checker.start()

    def cog_unload(self):
        self.checker.cancel()

    @tasks.loop(seconds=30.0)
    async def checker(self):
        channel = bot.get_channel(669750144484507648)
        notifs = await check_notif()
        if notifs:
            await channel.send(content="@everyone Whitestripe uploaded!")
            for notif in notifs:
                embed = discord.Embed(title=notif['title'], type="rich", description=notif['description'],
                                      url=notif['link'], color=discord.Colour.blue())
                embed.set_image(url=notif['thumbnail'])
                embed.set_author(name="Whitestripe", url="https://www.furaffinity.net/user/lionkinglover12/",
                                 icon_url="https://cdn.discordapp.com/avatars/237650755316613120/ad945ad99647fede2b4f493873501c81.png")
                embed.set_footer(text="Provided by huantian's soul",
                                 icon_url="https://cdn.discordapp.com/avatars/666830649444925450/2025ba70d07d3d41394f3becea865801.png")
                await channel.send(embed=embed)
            await reload_data('lionkinglover12')

    @checker.before_loop
    async def before_checker(self):
        print('waiting...')
        await self.bot.wait_until_ready()


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nothing(self, ctx):
        """This does nothing"""
        await ctx.send("This does nothing")


class FurAffinity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def reload(self, ctx):
        """Redownloads the FA data"""
        async with ctx.typing():
            await reload_data('lionkinglover12')
            await ctx.send("Done Downloading!")

    @commands.command()
    async def random(self, ctx):
        """Outputs a random FA submission"""
        random = await random_submission('lionkinglover12')

        embed = discord.Embed(title=random['title'], type="rich", description=h.handle(random['description']),
                              url=random['link'], color=discord.Colour.blue())
        embed.set_image(url=random['thumbnail'])
        embed.set_author(name="Whitestripe", url="https://www.furaffinity.net/user/lionkinglover12/",
                         icon_url="https://cdn.discordapp.com/avatars/237650755316613120/ad945ad99647fede2b4f493873501c81.png")
        embed.set_footer(text="Provided by huantian's soul",
                         icon_url="https://cdn.discordapp.com/avatars/666830649444925450/2025ba70d07d3d41394f3becea865801.png")

        await ctx.send(embed=embed)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx):
        """Joins a voice channel"""
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays from a url"""
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Now playing: {}'.format(player.title))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @commands.command()
    async def s(self, ctx, *, text: str):
        """Says text in voice channel"""
        tts = gTTS(text=ctx.author.name + ' says, ' + text, slow=False)
        tts.save('speech.mp3')

        player = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('speech.mp3'))
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    @play.before_invoke
    @s.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()


bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"),
                   description='huantian\'s soul: an AMAZING bot that does some text to speech and music. Also some FA stuff too.')


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('-------------------------')


bot.add_cog(Music(bot))
bot.add_cog(FurAffinity(bot))
bot.add_cog(General(bot))
bot.add_cog(FAChecker(bot))
bot.help_command.cog = General(bot)
bot.run(bot_config['token'])
