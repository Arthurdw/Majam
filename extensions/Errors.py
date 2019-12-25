import traceback
import discord
from datetime import timedelta
from util.core import formatter, data
from discord.ext import commands as cmd

em = formatter.embed_message

basic_formatter = {
    cmd.MissingRequiredArgument: "You forgot to define the argument \"**{error.param.name}**\".\n "
                                 "Use `!help {ctx.command.qualified_name}` for more information.",
    cmd.NoPrivateMessage: "This command **can't be used** in **private** messages.",
    cmd.DisabledCommand: "This command **is** currently **disabled**.",
    cmd.NotOwner: "This command can **only** be used by **the owner** of this bot."
}

ignore = [cmd.CommandNotFound, cmd.TooManyArguments]
catch_all = [cmd.CommandError]


class Errors(cmd.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cmd.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)
        catch_all = True
        if not isinstance(error, cmd.CommandOnCooldown):
            try: ctx.command.reset_cooldown(ctx)
            except AttributeError:
                pass
        for error_cls in ignore:
            if isinstance(error, error_cls):
                return
        for error_cls, format in basic_formatter.items():
            if isinstance(error, error_cls):
                await ctx.send(**em(format.format(error=error, ctx=ctx), type_="error"))
                return
        if isinstance(error, cmd.BotMissingPermissions):
            await ctx.send(**em(f"The bot is **missing** the following **permissions** `{', '.join(error.missing_perms)}`.",
                                type_="error"))
            return
        if isinstance(error, cmd.MissingPermissions):
            await ctx.send(**em(f"You are **missing** the following **permissions** `{', '.join(error.missing_perms)}`.",
                                type_="error"))
            return
        if isinstance(error, cmd.CommandOnCooldown):
            await ctx.send(**em(
                f"This command is currently **on cooldown** for `{str(timedelta(seconds=error.cooldown.per)).split('.')[0]}`.\n"
                f"Please **try again in** `{str(timedelta(seconds=error.retry_after)).split('.')[0]}`.",
                type_="error")
            )
            return
        if isinstance(error, cmd.CheckFailure):
            pass
        if isinstance(error, cmd.BadUnionArgument):
            pass
        if isinstance(error, cmd.BadArgument):
            if 'Converting to "' in str(error):
                converters = {
                    "int": "number"
                }
                conv = str(error).split('"')[1]
                parameter = str(error).split('"')[3]
                await ctx.send(**em(
                    f"The value you passed to **{parameter}** is not a valid **{converters.get(conv, conv)}**.",
                    type_="error"
                ))
                return

            if '" not found' in str(error):
                conv = str(error).split(" ")[0]
                value = str(error).split('"')[1]
                await ctx.send(**em(
                    f"**No {conv} found** that fits the value `{value}`.",
                    type_="error"
                ))
                return
        if catch_all:
            if isinstance(error, cmd.CommandError):
                await ctx.send(**em(str(error), type_="error"))
            if isinstance(error, discord.errors.Forbidden):
                pass
            else:
                count = data.get_stats("reports")[0][0] + 1
                report_channel = self.bot.get_channel(648076773417943047)
                rep = await report_channel.send(**em(title=f"Report: #{count}:",
                                                     content=f"**Command**: `{str(ctx.command.name).lower()}`\n"
                                                             f"**Author**: __Auto-Report__\n"
                                                             f"**Error**:\n```\n{error}\n```"))
                try:
                    await ctx.send(**em(error, type_="unex_error", extra=f"[#{count}]({rep.jump_url} "
                                                                         f"\"Auto-Report\")"))
                except Exception as e:
                    print(e)
                finally:
                    data.add_stats("reports")
                    _exception = traceback.format_exception(type(error), error, error.__traceback__)
                    exception = ""
                    for item in _exception:
                        exception += item + '\n'
                    error_channel = self.bot.get_channel(648222972213198859)
                    await error_channel.send(**em(title=f"Report: #{count}",
                                                  content=f"**Executable:** `{ctx.message.content}"
                                                          f"`\n**Error:** \n```{exception}```"))


def setup(bot):
    m = Errors(bot)
    bot.add_cog(m)
