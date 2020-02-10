from discord.ext import commands
import configparser

from errors import ConfigError
import cogs

config = configparser.ConfigParser()
config.read('config.ini')
bot_config = config['bot']

if not bot_config['token']:
    raise ConfigError('No token specified in config.')


bot = commands.Bot(command_prefix=commands.when_mentioned_or("?"),
                   description='huantian\'s soul: an AMAZING bot that does some text to speech and music. Also some FA stuff too.')


@bot.event
async def on_ready():
    print('Logged in as {0} ({0.id})'.format(bot.user))
    print('-------------------------')


bot.add_cog(cogs.Music(bot))
bot.add_cog(cogs.FurAffinity(bot))
bot.add_cog(cogs.General(bot))
bot.add_cog(cogs.FAChecker(bot))
bot.help_command.cog = cogs.General(bot)
bot.run(bot_config['token'])
