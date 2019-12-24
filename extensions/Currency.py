import discord
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

    @checks.management()
    @commands.command(name="rich", aliases=["addbal", "addbalance"])
    async def rich(self, ctx, user: discord.Member, amount: int):
        """Gives a user global money!"""
        try:
            data.add_global_bal(user_id=user.id, balance=amount)
            bank, cash, bank_max = self.get_global(user_id=user.id)
            await ctx.send(**em(content=f"Successfully added `{amount}` global balance to {user.mention}'s account!\n"
                                        f"Their current global balance:\n"
                                        f"Cash: {cash}\n"
                                        f"Bank: {bank}/{bank_max}"))
        except Exception as e:
            print(e)

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

    @commands.command(name="withdraw")
    async def withdraw(self, ctx, amount: int = None):
        """Withdraw cash from your bank account!"""
        if amount is None:
            await ctx.send(**em(type_="error",
                                content="You can't withdraw nothing!"))
            return
        bank, cash, bank_max = self.get_global(user_id=ctx.author.id)
        if amount > bank:
            await ctx.send(**em(content=f"That's more than what you have!\n You got {cash} coins! *(bank)*"))
        elif amount < 10:
            await ctx.send(**em(content="The minimum amount to withdraw is 10!"))
        else:
            data.withdraw_global_bal(user_id=ctx.author.id, amount=amount)
            await ctx.send(**em(content=f"Successfully withdrew {amount} coins from secure bank account!"))

    @commands.command(name="deposit")
    async def dep(self, ctx, amount: int = None):
        """Deposit cash in to your bank account!"""
        if amount is None:
            await ctx.send(**em(type_="error",
                                content="You can't deposit nothing!"))
            return
        bank, cash, bank_max = self.get_global(user_id=ctx.author.id)
        if amount > cash:
            await ctx.send(**em(content=f"That's more than what you have!\n You got {cash} coins! *(cash)*"))
        elif amount < 10:
            await ctx.send(**em(content="The minimum amount to deposit is 10!"))
        elif amount + bank > bank_max:
            await ctx.send(**em(content=f"Your bank account only supports {bank_max} coins!\n"
                                        f"Let your bank account support more by using commands or buy some! "
                                        f"*({data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)}buy)*"))
        else:
            data.deposit_global_bal(user_id=ctx.author.id, amount=amount)
            await ctx.send(**em(content=f"Successfully deposited {amount} coins to your secure bank account!"))


def setup(bot):
    bot.add_cog(Currency(bot))
