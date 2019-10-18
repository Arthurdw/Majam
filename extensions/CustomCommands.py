from discord.ext import commands
from util.core import data, formatter

em = formatter.embed_message


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="command", invoke_without_command=True)
    async def command(self, ctx):
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        await ctx.send(**em("Please use a valid sub-command."
                            f"\nSee the `{prefix}help command` command!"))


def setup(bot):
    bot.add_cog(CustomCommands(bot))
