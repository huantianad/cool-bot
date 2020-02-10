import discord
from discord.ext import commands
from faapi import reload_data, random_submission
import html2text


h = html2text.HTML2Text()


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
