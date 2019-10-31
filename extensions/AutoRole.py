import configparser
import discord
from discord.ext import commands
from util.core import data

config = configparser.ConfigParser()
config.read("config.cfg")


class VoiceChannelCreation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_join(self, member):
        pass


def setup(bot):
    bot.add_cog(VoiceChannelCreation(bot))
