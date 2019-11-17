import configparser
import time
import datetime
from discord.ext import commands
from util.core import data, formatter, process

average_latency = []
em = formatter.embed_message
start = time.time()

config = configparser.ConfigParser()
config.read("config.cfg")


class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx):
        global_message = data.get_global_message_count()[0][0]
        global_commands = data.get_global_command_count()[0][0]
        global_custom_commands = data.get_global_custom_command_count()[0][0]
        guilds = str(len(self.bot.guilds))
        members = str(len(set(self.bot.get_all_members())) - 1)
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - start))))
        first = time.perf_counter()
        await ctx.trigger_typing()
        last = time.perf_counter()
        response_time = round((last-first)*1000, 2)
        await ctx.send(**em(title="Statistics:",
                            content="**Bot:**\n"
                                    f"Uptime: `{uptime}`\n"
                                    f"Members: `{members}`\n"
                                    f"Guilds: `{guilds}`\n"
                                    f"Messages: `{global_message}`\n"
                                    f"Commands: `{global_commands}`\n"
                                    f"Custom Commands: `{global_custom_commands}`\n\n"
                                    f"**Ping:**\n"
                                    f"Latency: `{round(self.bot.latency * 1000, 2)}` ms\n"
                                    f"Response Time: `{response_time}` ms\n\n"))

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - start))))
        await ctx.send(**em(content=f"Uptime: `{uptime}`"))

    @commands.command(name="ping")
    async def ping(self, ctx):
        first = time.perf_counter()
        await ctx.trigger_typing()
        last = time.perf_counter()
        response_time = round((last-first)*1000, 2)
        await ctx.send(**em(content=f"Latency: `{round(self.bot.latency * 1000, 2)}` ms\n"
                                    f"Response Time: `{response_time}` ms\n\n"))

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            data.add_global_command_count()
        else:
            data.add_global_message_count()


def setup(bot):
    bot.add_cog(Statistics(bot))
