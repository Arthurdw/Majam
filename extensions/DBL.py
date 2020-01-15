import dbl
import discord
import asyncio
from DBLMR import DBLMR
from discord.ext import commands
from util.core import formatter, data, process

em = formatter.embed_message
client = DBLMR.Client("232182858251239424-5je6Iio0NAfz6fBZRYNy2qR6qt7ifoap")

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

    @commands.group(name="auctions", aliases=["auc"], invoke_without_command=True)
    async def auctions(self, ctx):
        """Receive stats about DBL auctions."""
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        await ctx.send(**em(f"Please use a valid sub-command.\nSee the `{prefix}help {ctx.command.qualified_name}`!"))

    @commands.cooldown(1, 10, commands.BucketType.user)
    @auctions.command(name="bidders")
    async def bidders(self, ctx, amount: int = None):
        """Display DBL auctions bidders. (weekly)"""
        ctx_message = await ctx.send(**em("Fetching data."))
        bidders = client.auctions.bidders
        if amount is None:
            amount = len(bidders)
        if len(bidders) == 0:
            await ctx.send(**em("There are currently no bidders!\n"
                                "Try again later!"))
        else:
            counter, message = 1, []
            for bidder in bidders:
                message.append(f"{counter} | ${bidder.bet} | {bidder.name} (`{bidder.id}`)")
                if counter >= amount:
                    leftover = len(bidders) - counter
                    if leftover != 0:
                        message.append(str(leftover) + " more...")
                    break
                counter += 1
            sliced = formatter.paginate("\n".join(message))
            for count in range(len(sliced)):
                title, end, footer = discord.Embed.Empty, "", False
                if count == 0:
                    title = f"Current bidders. ({len(bidders)})"
                if count == len(sliced) - 1:
                    end = f"\n\nProvided by the [DBLMR](https://github.com/Arthurdw/DBLMR \"DBLMR module github\") module!"
                    footer = True
                await ctx.send(**em(title=title, content=sliced[count] + end, footer=footer))
            try:
                await ctx_message.delete()
            except: pass

    @commands.cooldown(1, 10, commands.BucketType.user)
    @auctions.command(name="bets")
    async def bets(self, ctx, amount: int = None):
        """Display DBL auctions bets. (weekly)"""
        ctx_message = await ctx.send(**em("Fetching data."))
        bets = client.auctions.bets
        if amount is None:
            amount = len(bets)
        if len(bets) == 0:
            await ctx.send(**em("There are currently no bets!\n"
                                "Try again later!"))
        else:
            counter, message = 1, []
            for bet in bets:
                message.append(f"{counter} | ${bet.bet} | {bet.slot} | {bet.item} | {bet.name} (`{bet.id}`)")
                if counter >= amount:
                    leftover = len(bets) - counter
                    if leftover >= 0:
                        message.append(str(leftover) + " more...")
                    break
                counter += 1
            sliced = formatter.paginate("\n".join(message))
            for count in range(len(sliced)):
                title, end, footer = discord.Embed.Empty, "", False
                if count == 0:
                    title = f"Current bets. ({len(bets)})"
                if count == len(sliced) - 1:
                    end = f"\n\nProvided by the [DBLMR](https://github.com/Arthurdw/DBLMR \"DBLMR module github\") module!"
                    footer = True
                await ctx.send(**em(title=title, content=sliced[count] + end, footer=footer))
            try:
                await ctx_message.delete()
            except: pass

    @commands.command(name="dbl")
    async def dbl(self, ctx, *, bot: discord.Member = None):
        if bot is None:
            await ctx.send(**em(title="DBL/DSL stats:",
                                content=f"Bots: {client.stats.bots}\n"
                                        f"Sum of all server counts: {client.stats.servers}"))
            return
        if not bot.bot:
            await ctx.send(**em(content="Ehmm.\nThis **USER** is not listed on DBL...\n\nWait wut, user? Why you want "
                                        "to get bot information from a user lol!?"))
            return
        try:
            bot_info = await self.dblpy.get_bot_info(bot.id)
            mr_bot = client.bot(bot.id)
            web, support, git = bot_info["website"], bot_info["support"], bot_info["github"]
            extra_string = " | "
            params = [f'[Vote](https://top.gg/bot/{bot.id}/vote "Vote for {bot}")',
                      f'[Invite](https://discordapp.com/oauth2/authorize?client_id={bot.id}&permissions=8&scope=bot "Invite {bot}")']
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
            notice = f'Notice: {mr_bot.notice}\n' or ''
            await ctx.send(**em(author=(bot.name, f'https://top.gg/bot/{bot.id}', bot.avatar_url),
                                title="Bot info:",
                                content=f'**Bot:** {bot_info["username"]}#{bot_info["discriminator"]} *({bot_info["id"]})*\n'
                                        f'**Short Description:**\n```{bot_info["shortdesc"]}```\n'
                                        f'**Prefix:** `{bot_info["prefix"]}`\n'
                                        f'**Upvotes:** `{bot_info["monthlyPoints"]}` *(`{bot_info["points"]}`)*,'
                                        f' {mr_bot.daily} today. (Might have some delay)\n'
                                        f'{server_count}**Owner(s):** {owners}\n**Tags:** {tag_list}\n**Libary:** '
                                        f'{bot_info["lib"]}\n**Certified:** '
                                        f'{str(bot_info["certifiedBot"]).replace("True", "Yes").replace("False", "No")}\n'
                                        f'**Added bot on:** {formatter.convert_time(bot_info["date"])}\n\n'
                                        f'{notice}\n**Rank:**\n```\nDaily: #{mr_bot.rank.daily}\nMonthly: #'
                                        f'{mr_bot.rank.monthly}\nAll-Time: #{mr_bot.rank.all}\nServers: #'
                                        f'{mr_bot.rank.servers}\n```\n'
                                        f"**Extra:**\n{extra_string}"))
        except dbl.errors.NotFound:
            await ctx.send(**em("This bot isn't listed on DBL! *(yet?)*"))

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        print(data)
        print(type(data))


def setup(bot):
    bot.add_cog(DiscordBotsOrgAPI(bot))
