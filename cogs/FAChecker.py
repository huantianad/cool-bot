import discord
from discord.ext import commands, tasks
from faapi import check_notif, reload_data
import html2text

h = html2text.HTML2Text()


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
                embed = discord.Embed(title=notif['title'], type="rich", description=h.handle(notif['description']),
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
