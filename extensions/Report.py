from discord.ext import commands
from util.core import formatter, data

em = formatter.embed_message


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command(name="report")
    async def report(self, ctx, command=None, *, message=None):
        """Report bugged commands!"""
        if command is None:
            await ctx.send(**em(type_="error",
                                content=f"Please provide a command & a message for the report!!"))
            ctx.command.reset_cooldown(ctx)
            return
        elif message is None:
            await ctx.send(**em(type_="error",
                                content=f"Please provide a message for the report!!"))
            ctx.command.reset_cooldown(ctx)
            return
        command = self.bot.get_command(str(command).lower())
        report_channel = self.bot.get_channel(648076773417943047)
        if command is None:
            await ctx.send(**em(type_="error",
                                content="Couldn't find that command!\n"
                                        "Please try again with a valid command!"))
            ctx.command.reset_cooldown(ctx)
        else:
            data.add_stats("reports")
            count = data.get_stats("reports")[0][0]
            _re_l = await report_channel.send(**em(title=f"Report: #{count}:",
                                                   content=f"**Command**: `{str(command).lower()}`\n"
                                                           f"**Author**: {ctx.author.mention} ({ctx.author.id})\n"
                                                           f"**Message**:\n```\n{str(message).lower().capitalize()}\n```"))
            await ctx.send(**em(title="Success!",
                                content=f"Successfully send a report for the command: `{str(command).lower()}`!\n"
                                        f"Report message:\n```\n{str(message).lower().capitalize()}\n```\n"
                                        "*(Find your report in [#report](https://discord.gg/P29AqVa \"Alexi's discord"
                                        f" bot support server!\") [[#{count}]({_re_l.jump_url} \"#{count} report\")])*"))


def setup(bot):
    bot.add_cog(Report(bot))
