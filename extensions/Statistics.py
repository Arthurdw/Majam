import configparser
from discord.ext import commands
from util.core import data, formatter

em = formatter.embed_message

config = configparser.ConfigParser()
config.read("config.cfg")


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx):
        global_message = data.get_global_message_count()[0][0]
        global_commands = data.get_global_command_count()[0][0]
        await ctx.send(**em(title="Statistics:",
                            content="**Global:**\n"
                                    f"Messages: `{global_message}`\n"
                                    f"Commands: `{global_commands}`"))

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            data.add_global_command_count()
        else:
            data.add_global_message_count()


def setup(bot):
    bot.add_cog(Statistics(bot))
