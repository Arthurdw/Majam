import configparser
from discord.ext import commands
from util.core import data, formatter

config = configparser.ConfigParser()
config.read("config.cfg")
em = formatter.embed_message


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def default(self, ctx):
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        return f"Please use a valid sub-command.\nSee the `{prefix}help {ctx.command.qualified_name}`!"

    @commands.group(name="command", invoke_without_command=True)
    async def command(self, ctx):
        """Commands group command!"""
        await ctx.send(**em(self.default(ctx)))

    @command.command(name="add")
    async def add(self, ctx, *, command=None):
        """Add a custom command!
        ⇒ !command add foo return bar
        ⇒ !foo
        ⇐ bar"""
        if command is None:
            await ctx.send(**em(content="Please provide a command name and a response!\n"
                                        "For more information you can check out the "
                                        f"[docs]({config['DOCS']['customCommands']} \"Alexi Documentation\")."))
        elif 'return' not in str(command).lower().split(' '):
            await ctx.send(**em(content="Please use the correct syntax to add a command.\n"
                                        "For more information you can check out the "
                                        f"[docs]({config['DOCS']['customCommands']} \"Alexi Documentation\")."))
        else:
            name = str(command).lower()
        # elif data.get_command(ctx.message.guild.id):
        #     pass


def setup(bot):
    bot.add_cog(CustomCommands(bot))
