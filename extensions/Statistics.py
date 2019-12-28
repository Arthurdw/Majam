import configparser
import time
import datetime
import random
from discord.ext import commands
from util.core import data, formatter, GitHub

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
        from extensions.Main import version
        fetching = await ctx.send(**em(content="Fetching data!\nPlease wait..."))
        first = time.perf_counter()
        await ctx.trigger_typing()
        last = time.perf_counter()
        global_message, global_commands = data.get_stats("messages")[0][0], data.get_stats("command")[0][0]
        global_custom_commands = data.get_stats("custom-command")[0][0]
        custom_commands = len(data.fetch_all(config["DATABASE"]["commandsDB"]))
        auto_roles = len(data.fetch_all(config["DATABASE"]["autoRoleDB"]))
        guilds, members = str(len(self.bot.guilds)), str(len(set(self.bot.get_all_members())) - 1)
        uptime = str(datetime.timedelta(seconds=int(round(time.time() - start))))
        latest = GitHub.version()
        if version == latest:
            final_v = f"`{version}` *(latest)*"
        else:
            final_v = f"`{version}` *(old)*\nLatest version: `{latest}` *(Restart may occur soon!)*"
        response_time = round((last-first)*1000, 2)
        await fetching.edit(**em(title="Statistics:",
                                 content="**Bot:**\n"
                                         f"Uptime: `{uptime}`\n"
                                         f"Members: `{members}`\n"
                                         f"Guilds: `{guilds}`\n"
                                         f"Messages: `{global_message}`\n"
                                         f"Auto-Roles: `{auto_roles}`\n"
                                         f"Custom commands:  `{custom_commands}`\n"
                                         f"Commands executed: `{global_commands}`\n"
                                         f"Custom Commands executed: `{global_custom_commands}`\n"
                                         f"Version: {final_v}\n\n"
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
            if random.choice([True, False]):
                data.add_max_bank_bal(message.author.id, 1)
        else:
            data.add_stats("messages")


def setup(bot):
    bot.add_cog(Statistics(bot))
