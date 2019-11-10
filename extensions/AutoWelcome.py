import configparser
from discord.ext import commands
from util.core import data, formatter

em = formatter.embed_message

config = configparser.ConfigParser()
config.read("config.cfg")


class AutoWelcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_join(self, member):
        # Support guild:
        if member.guild.id == 634141277788831795:
            channel = self.bot.get_channel(638375697991204864)
            if member.bot:
                await channel.send(**em(title=f"Welcome {member.name}",
                                        content=f"Since you're a bot, hello beep beep!",
                                        footer=False))
            else:
                await channel.send(**em(title=f"Welcome {member.name}",
                                        content="Please carefully read our <#638375742782046220>!\n"
                                                "For support please read our <#638376564169506836> first!\n"
                                                "Cant find your answer? Feel free to ask it in <#638376489271951400>!\n"
                                                f"\nEnjoy your time here {member.mention}!\n",
                                        footer=False))


def setup(bot):
    bot.add_cog(AutoWelcome(bot))
