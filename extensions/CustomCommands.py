from discord.ext import commands
from util.core import data, formatter

em = formatter.embed_message


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def default(self, ctx):
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        return f"Please use a valid sub-command.\nSee the `{prefix}help {ctx.command.qualified_name}`!"

    @commands.group(name="command", invoke_without_command=True)
    async def command(self, ctx):
        CustomCommands.default(self, ctx)


def setup(bot):
    bot.add_cog(CustomCommands(bot))
