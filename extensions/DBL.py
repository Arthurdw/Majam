import dbl
import discord
from discord.ext import commands
import asyncio
from util.core import formatter

em = formatter.embed_message


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

    @commands.command(name="dbl")
    async def dbl(self, ctx, bot: discord.Member = None):
        if bot is None:
            await ctx.send(**em(content="Can't lookup nothing if you provide nothing! :/"))
            return
        if not bot.bot:
            await ctx.send(**em(content="Ehmm.\nThis **USER** is not listed on DBL...\n\nWait wut, user? Why you want "
                                        "to get bot information from a user lol!?"))
            return
        try:
            bot_info = await self.dblpy.get_bot_info(bot.id)
            web, support, git = bot_info["website"], bot_info["support"], bot_info["github"]
            extra_string = " | "
            params = [f'[Vote](https://top.gg/bot/{bot.id}/vote "Vote for {bot}")',
                      f'[Invite]({bot_info["invite"]} "Invite {bot}")']
            if web is not None:
                params.append(f"[Website]({web} \"{bot.name}'s website!\")")
            if support is not None:
                params.append(f"[Support Server](https://discord.gg/{support} \"{bot.name}'s support server!\")")
            if git is not None:
                params.append(f"[Github]({git} \"{bot.name}'s github!\")")
            extra_string = extra_string.join(params)
            try:
                count = str(bot_info["server_count"])
                if count == "[]":
                    count = "No guilds!"
            except KeyError:
                count = "No guilds!"
            server_count = f"**Server count:** `{count}`\n"
            owner_list = []
            owners = ", "
            tag_list = ", "
            tag_list = tag_list.join(bot_info['tags'])
            for owner in bot_info["owners"]:
                owner_list.append(f"<@{owner}>")
            owners = owners.join(owner_list)
            await ctx.send(**em(author=(bot.name, f'https://top.gg/bot/{bot.id}', bot.avatar_url),
                                title="Bot info:",
                                content=f'**Bot:** {bot_info["username"]}#{bot_info["discriminator"]} *({bot_info["id"]})*\n'
                                        f'**Short Description:**\n```{bot_info["shortdesc"]}```\n'
                                        f'**Prefix:** `{bot_info["prefix"]}`\n'
                                        f'**Upvotes:** `{bot_info["monthlyPoints"]}` *(`{bot_info["points"]}`)*\n'
                                        f'{server_count}**Owner(s):** {owners}\n**Tags:** {tag_list}\n**Libary:** '
                                        f'{bot_info["lib"]}\n**Certified:** '
                                        f'{str(bot_info["certifiedBot"]).replace("True", "Yes").replace("False", "No")}\n'
                                        f'**Added bot on:** {formatter.convert_time(bot_info["date"])}\n\n'
                                        f"**Extra:**\n{extra_string}"))
        except dbl.errors.NotFound:
            await ctx.send(**em("This bot isn't listed on DBL! *(yet?)*"))

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        print(data)


def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
