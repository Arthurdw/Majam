import discord
import random
import asyncio
from discord.ext import commands
from util.core import formatter, data

em = formatter.embed_message


class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="flip", aliases=["coin"])
    async def coinflip(self, ctx, bet: int, side=None):
        """Bet on a coinflip."""
        if side is None:
            await ctx.send(**em(type_="error",
                                content="Please provide a side your flip's on!\n"
                                        "Sides: heads *(H)* tails *(T)*"))
            ctx.command.reset_cooldown(ctx)
            return
        elif bet < 10:
            await ctx.send(**em("The minimum bet is 10!"))
            ctx.command.reset_cooldown(ctx)
            return
        elif bet > data.get_global_bal(ctx.author.id)[0][0]:
            await ctx.send(**em("You can't bet what you don't have!\n"
                                f"You have `{data.get_global_bal(ctx.author.id)[0][0]}` coins!"))
            ctx.command.reset_cooldown(ctx)
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

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command(name="slots")
    async def slots(self, ctx, bet: int):
        """Gamble with slots!"""
        if bet < 100:
            await ctx.send(**em("The minimum bet is 100!"))
            ctx.command.reset_cooldown(ctx)
            return
        spinning = await ctx.send(**em("Spinning weel!"))
        slot_icons = ("<:Majam:659018214633635843>", "<:DevBot:659019961334890537>",
                      "<:CheekiBreeki:659018436524900383>", "💩", "🤡", "🤑", "💸", "💰", "💳", "💵", "💲")

        choices, first, last, win, selected = (), (), (), 0, " "
        for _ in range(5):
            choices += (random.choice(slot_icons),)
            first += (random.choice(slot_icons),)
            last += (random.choice(slot_icons),)
        for choice in choices:
            if choice == "<:Majam:659018214633635843>" or choice == "<:DevBot:659019961334890537>": win += 2
            elif choice == "<:CheekiBreeki:659018436524900383>": win += 1.5
            elif choice == "💩" or choice == "🤡": win -= 2.5
            elif choice == "🤑" or choice == "💳": win += 0.2
            elif choice == "💸" or choice == "💰": win += 0.5
            elif choice == "💵" or choice == "💲": win += 1
        await asyncio.sleep(2)
        data.add_global_bal(ctx.author.id, round(bet*win, 2))
        await spinning.edit(**em(title="Slots:",
                                 content=f"{selected.join(first)}\n{selected.join(choices)}<--\n{selected.join(last)}\n"
                                         f"Your bet got multiplied by `{round(win, 2)}`. *(`{round(bet*win, 2)}`)*"))


def setup(bot):
    bot.add_cog(Gambling(bot))
