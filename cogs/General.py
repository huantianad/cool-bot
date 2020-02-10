import discord
from discord.ext import commands


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nothing(self, ctx):
        """This does nothing"""
        await ctx.send("This does nothing")
