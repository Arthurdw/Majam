import datetime
import configparser
from discord.ext import commands
from util.core import data, formatter, checks, GitHub

config = configparser.ConfigParser()
config.read("config.cfg")
em = formatter.embed_message
version = GitHub.version()


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def default(self, ctx):
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        return f"Please use a valid sub-command.\nSee the `{prefix}help {ctx.command.qualified_name}`!"

    @checks.management()
    @commands.group(name="dev", invoke_without_command=True)
    async def development(self, ctx):
        """All bot dev commands!"""
        await ctx.send(**em(self.default(ctx)))

    @development.command(name='version')
    async def version(self, ctx):
        embed = formatter.embed_message(content=f"Currently running on version: \n`{version}`", footer=False)["embed"]
        embed.set_footer(
            text=(config["UTILITY"]["default_footer_message"])[1:-8],
            icon_url="https://cdn.discordapp.com/avatars/634141001769943090/bb49774a1684d9cd1f1958039a25b89c.webp")
        embed.timestamp = datetime.datetime.now()
        await ctx.send(embed=embed)

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
        """Prefix related commands"""
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        await ctx.send(**em(self.default(ctx) + f"\nCurrent prefix: `{prefix}` or just mention me!"))

    @prefix.command(name="set")
    async def set(self, ctx, *, prefix):
        """Add/Set your custom prefix"""
        if len(prefix) >= 10:
            await ctx.send(**em(content="The prefix shouldn't exceed 10 characters!"))
            return
        try:
            data.set_prefix(ctx.message.guild.id, ctx.message.author.id, prefix)
            await ctx.send(**em(content=f"Successfully set the server prefix to `{prefix}`"))
        except Exception as e:
            print(e)
            await ctx.send(**em(content="Oh an error occurred, this shouldn't happen please contact the "
                                        "core developer `Arthur#0002`!\n"
                                        f"Exception type: `{type(e).__name__}`\n"
                                        f"Arguments: \n```\n{e.args}\n```"))


def setup(bot):
    bot.add_cog(Main(bot))
