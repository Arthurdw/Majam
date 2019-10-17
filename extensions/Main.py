from discord.ext import commands


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="test")
    async def test(self, ctx):
        await ctx.send("hoi")


def setup(bot):
    bot.add_cog(Main(bot))
