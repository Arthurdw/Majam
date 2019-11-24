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
        global_message, global_commands = data.get_stats("messages")[0][0], data.get_stats("command")[0][0]
        global_custom_commands = data.get_stats("custom-command")[0][0]
        custom_commands = len(data.fetch_all(config["DATABASE"]["commandsDB"]))
        guilds, members = str(len(self.bot.guilds)), str(len(set(self.bot.get_all_members())) - 1)
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
                                    f"Custom commands:  `{custom_commands}`\n"
                                    f"Commands executed: `{global_commands}`\n"
                                    f"Custom Commands executed: `{global_custom_commands}`\n\n"
                                    f"**Ping:**\n"
                                    f"Latency: `{round(self.bot.latency * 1000, 2)}` ms\n"
                                    f"Response Time: `{response_time}` ms\n\n"))

    @commands.command(name="uptime")
    async def uptime(self, ctx):
        await ctx.send(**em(content=f"Uptime: `{str(datetime.timedelta(seconds=int(round(time.time() - start))))}`"))

    @commands.command(name="ping")
    async def ping(self, ctx):
        first = time.perf_counter()
        await ctx.trigger_typing()
        last = time.perf_counter()
        await ctx.send(**em(content=f"Latency: `{round(self.bot.latency * 1000, 2)}` ms\n"
                                    f"Response Time: `{round((last-first)*1000, 2)}` ms\n\n"))

    @commands.Cog.listener()
    async def on_message(self, message):
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            data.add_stats("command")
        else:
            data.add_stats("messages")


def setup(bot):
    bot.add_cog(Statistics(bot))
