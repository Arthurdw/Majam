import discord
from discord.ext import commands


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO:
    #   Add competitive leveling system!

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.content) > 10:
            pass  # Add exp to user.


def setup(bot):
    bot.add_cog(Levels(bot))
