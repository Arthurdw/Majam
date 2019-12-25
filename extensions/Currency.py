import discord
import asyncio
import random
from discord.ext import commands
from util.core import checks, formatter, data

em = formatter.embed_message


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def default(self, ctx):
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        return f"Please use a valid sub-command.\nSee the `{prefix}help {ctx.command.qualified_name}`!"

    @staticmethod
    def get_global(user_id: int):
        cash, bank, bank_max = "**ERROR**", "**ERROR**", "**ERROR**"
        bank_balance = data.get_global_bal(user_id)
        max_bank = data.get_global_max_bank(user_id)
        if bank_balance:
            bank, cash = bank_balance[0][1], bank_balance[0][0]
        if max_bank:
            bank_max = max_bank[0][0]
        return [bank, cash, bank_max]

    @commands.command(name="baltop")
    async def bal_top(self, ctx):
        """Displays the top 10 richest people!"""
        top_list, final, count = [], "\n", 0
        for user, bank, cash in data.get_baltop(10):
            count += 1
            top_list.append(f"{count}\t-\t{discord.utils.get(self.bot.get_all_members(), id=user)}*(`{user}`)*\t|\tcash: "
                            f"`{cash}`")
        await ctx.send(**em(title="Top global balances:",
                            content=f"{final.join(top_list)}\n\nDon't see a guy in here?\nUse "
                                    f"`{data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)}bal user`"))

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="beg")
    async def beg(self, ctx):
        """Beg for some coins you silly!"""
        messages = ["Here get some coins!\n(`{coins}`)", "You in need of some cash?\nHaha get some coins!\n(`{coins}`)"]
        if random.choice([True, False]):
            await ctx.send(**em(random.choice(messages).format(coins=random.randint(2, 50))))
        else:
            await ctx.send(**em("Meh, no coins for you!"))

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.command(name="mine")
    async def mine(self, ctx):
        """Mine some coins. :)"""
        award = random.choice([random.randint(0, 50), random.randint(25, 100), random.randint(50, 200),
                              random.choice([
                                  random.randint(75, 300),
                                  random.randint(250, 700),
                                  random.choice([random.randint(500, 1000), random.randint(700, 1300)])]
                              )])
        data.add_global_bal(ctx.author.id, award)
        await ctx.send(**em(f"You have been given {award} coins for mining!"))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="send", aliases=["give"])
    async def send(self, ctx, user: discord.Member, amount: int):
        """Give some cash coins to a friend!"""
        bank, cash, bank_max = self.get_global(user_id=ctx.author.id)
        if amount < 10:
            await ctx.send(**em("The minimum you can give to a user is 10 coins!"))
            ctx.command.reset_cooldown(ctx)
        elif amount > cash:
            await ctx.send(**em("You do not have significant cash available!"))
            ctx.command.reset_cooldown(ctx)
        else:
            message = await ctx.send(**em(content=f"Transferring {amount} coins to {user.mention}!"))
            data.remove_global_bal(ctx.author.id, amount)
            data.add_global_bal(user.id, amount)
            await asyncio.sleep(3)
            await message.edit(**em(f"Successfully transferred {amount} to {user.mention}!\n"
                                    f"Transfer id: #`{str(hex(message.id))[2:]}`"))

    @checks.management()
    @commands.command(name="rich", aliases=["addbal", "addbalance"])
    async def rich(self, ctx, user: discord.Member, amount: int):
        """Gives a user global money!"""
        data.add_global_bal(user_id=user.id, balance=amount)
        bank, cash, bank_max = self.get_global(user_id=user.id)
        await ctx.send(**em(content=f"Successfully added `{amount}` global balance to {user.mention}'s account!\n"
                                    f"Their current global balance:\n"
                                    f"Cash: {cash}\n"
                                    f"Bank: {bank}/{bank_max}"))

    @checks.management()
    @commands.command(name="poor", aliases=["delbal", "delbalance", "rembal", "rembalance"])
    async def poor(self, ctx, user: discord.Member, amount: int):
        """Takes a user's global money!"""
        try:
            data.remove_global_bal(user_id=user.id, balance=amount)
            bank, cash, bank_max = self.get_global(user_id=user.id)
            await ctx.send(**em(content=f"Successfully removed `{amount}` global balance from {user.mention}'s "
                                        f"account!\nTheir current global balance:\n"
                                        f"Cash: {cash}\n"
                                        f"Bank: {bank}/{bank_max}"))
        except Exception as e:
            print(e)

    @commands.command(name="bal", aliases=["currency", "balance"])
    async def balance(self, ctx, user: discord.Member = None):
        """This will display a user their current balance!"""
        if user is None:
            user = ctx.message.author
        bank, cash, bank_max = self.get_global(user_id=user.id)
        await ctx.send(**em(title=f"{user.display_name}'s balance:",
                            content="Global balance:\n"
                                    f"Cash: {cash}\n"
                                    f"Bank: {bank}/{bank_max}"))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="withdraw")
    async def withdraw(self, ctx, amount: int = None):
        """Withdraw cash from your bank account!"""
        if amount is None:
            await ctx.send(**em(type_="error",
                                content="You can't withdraw nothing!"))
            ctx.command.reset_cooldown(ctx)
            return
        bank, cash, bank_max = self.get_global(user_id=ctx.author.id)
        if amount > bank:
            await ctx.send(**em(content=f"That's more than what you have!\n You got {cash} coins! *(bank)*"))
            ctx.command.reset_cooldown(ctx)
        elif amount < 10:
            await ctx.send(**em(content="The minimum amount to withdraw is 10!"))
            ctx.command.reset_cooldown(ctx)
        else:
            data.withdraw_global_bal(user_id=ctx.author.id, amount=amount)
            await ctx.send(**em(content=f"Successfully withdrew {amount} coins from secure bank account!"))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="deposit")
    async def dep(self, ctx, amount: int = None):
        """Deposit cash in to your bank account!"""
        if amount is None:
            await ctx.send(**em(type_="error",
                                content="You can't deposit nothing!"))
            ctx.command.reset_cooldown(ctx)
            return
        bank, cash, bank_max = self.get_global(user_id=ctx.author.id)
        if amount > cash:
            await ctx.send(**em(content=f"That's more than what you have!\n You got {cash} coins! *(cash)*"))
            ctx.command.reset_cooldown(ctx)
        elif amount < 10:
            await ctx.send(**em(content="The minimum amount to deposit is 10!"))
            ctx.command.reset_cooldown(ctx)
        elif amount + bank > bank_max:
            await ctx.send(**em(content=f"Your bank account only supports {bank_max} coins!\n"
                                        f"Let your bank account support more by using commands or buy some! "
                                        f"*({data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)}buy)*"))
            ctx.command.reset_cooldown(ctx)
        else:
            data.deposit_global_bal(user_id=ctx.author.id, amount=amount)
            await ctx.send(**em(content=f"Successfully deposited {amount} coins to your secure bank account!"))


def setup(bot):
    bot.add_cog(Currency(bot))
