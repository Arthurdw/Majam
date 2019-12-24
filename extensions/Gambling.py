import discord
import random
from discord.ext import commands
from util.core import formatter, data

em = formatter.embed_message


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="flip", aliases=["coin"])
    async def coinflip(self, ctx, bet: int, side=None):
        if side is None:
            await ctx.send(**em(type_="error",
                                content="Please provide a side your flip's on!\n"
                                        "Sides: heads *(H)* tails *(T)*"))
            return
        elif bet < 10:
            await ctx.send(**em("The minimum bet is 10!"))
            return
        elif bet > data.get_global_bal(ctx.author.id)[0][0]:
            await ctx.send(**em("You can't bet what you don't have!\n"
                                f"You have `{data.get_global_bal(ctx.author.id)[0][0]}` coins!"))
            return
        _heads, _tails = False, False
        side = str(side).lower()
        tails = ("tails", "tail", "t")
        heads = ("heads", "head", "h")
        for count in range(len(tails)):
            if tails[count] == side:
                _tails = True
            if heads[count] == side:
                _heads = True
        if not _tails and not _heads:
            await ctx.send(**em(content="Seems like the chosen side wasn't valid!"))
        else:
            win_winning_side, los_winning_side = heads[0].capitalize(), tails[0].capitalize()
            if _tails:
                win_winning_side, los_winning_side = tails[0].capitalize(), heads[0].capitalize()
            if _heads is random.choice([True, False]):
                await ctx.send(**em(f"You just doubled your bet. *(`{bet}` --> `{bet*2}`)*\n"
                                    f"Winning side: {win_winning_side}"))
                data.add_global_bal(ctx.author.id, bet)
            else:
                await ctx.send(**em(f"You just lost your bet! *(`{bet}`)*\n"
                                    f"Winning side: {los_winning_side}"))
                data.remove_global_bal(ctx.author.id, bet)


def setup(bot):
    bot.add_cog(Gambling(bot))
