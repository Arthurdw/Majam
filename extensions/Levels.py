import discord
from discord.ext import commands


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # TODO:
    #   Add competitive leveling system!


def setup(bot):
    bot.add_cog(Levels(bot))
