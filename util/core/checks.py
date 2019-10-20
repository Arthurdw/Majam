import configparser
from discord.ext import commands

config = configparser.ConfigParser()
config.read("config.cfg")


def management():
    def check(ctx):
        if str(ctx.message.author.id) in str(config["UTILITY"]["management"]).split(","):
            return True
        return False
    return commands.check(check)
