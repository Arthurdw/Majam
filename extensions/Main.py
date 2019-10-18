from discord.ext import commands
from util.core import data, formatter

em = formatter.embed_message


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
        """Prefix related commands"""
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        await ctx.send(**em("Please use a valid sub-command."
                            f"\nSee the `{prefix}help` command!\nCurrent prefix: {prefix} or just mention me!"))

    @prefix.command(name="set")
    async def set(self, ctx, *, prefix):
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
