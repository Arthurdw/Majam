import dbl
from discord.ext import commands
import asyncio


class DiscordBotsOrgAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjYzNDE0MTAwMTc2OTk0MzA5MCIsImJvdCI6dHJ1ZSwiaWF0IjoxNTczODM5MTY3fQ.pPF9YWdH-xZRdnUftU24oa2_kVTeCf1e00tihFuYuEo"
        self.dblpy = dbl.DBLClient(self.bot, self.token)
        self.updating = self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        while not self.bot.is_closed():
            try:
                await self.dblpy.post_guild_count()
            except Exception as e:
                print(e)
            await asyncio.sleep(1800)


def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
