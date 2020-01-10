import discord
import glob
import asyncio
from discord.ext import commands
from util.core import formatter, data
from util.core.process import exe_walker

em = formatter.embed_message


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, *, command=None):
        """Help command!"""
        help_const, sub_const, message, final = [], [], ", ", "\n"
        if command is None:
            choice = await ctx.send(**em("Would you like to receive the help message in private messages or in this "
                                         "channel?\nClick on the <:Chat:659338796181225474> emoji to let me post it in "
                                         "chat.\nClick on the <:DM:659338796550193171> emoji to let me post it in DM."))
            try:
                await choice.add_reaction(":Chat:659338796181225474")
                await choice.add_reaction(":DM:659338796550193171")
            except: pass

            def check(_reaction, _user):
                return _user == ctx.author and (str(_reaction.emoji) == "<:Chat:659338796181225474>" or
                                                str(_reaction.emoji) == "<:DM:659338796550193171>")

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                try:
                    await choice.edit(**em("You didn't react or to late. *(60s+)*"))
                except discord.errors.NotFound:
                    await ctx.send(**em("You didn't react or to late. *(60s+)*"))
                try: await choice.clear_reactions()
                except: pass
            else:
                receiver = ctx
                if str(reaction) == "<:DM:659338796550193171>":
                    receiver = ctx.author
                for extension in glob.glob("extensions/*.py"):
                    fixed_extension = extension.replace("extensions/", "")[:-3]
                    if fixed_extension != "DBL" and fixed_extension != "Help":
                        cog = self.bot.get_cog(fixed_extension)
                        _commands = cog.get_commands()
                        walker = [c for c in cog.walk_commands()]
                        if walker:
                            sub_const, count = exe_walker(cog)
                            help_const.append(f"**{cog.qualified_name} [`{count}`]**:\n{message.join(sub_const)}\n")
                            sub_const = []
                prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
                sliced = formatter.paginate(final.join(help_const))
                try:
                    for count in range(len(sliced)):
                        title, end, footer = discord.Embed.Empty, "", False
                        if count == 0:
                            title = "Help:"
                        if count == len(sliced) - 1:
                            end = f"\n*Type {prefix}help command* for more details!"
                            footer = True
                        await receiver.send(**em(title=title,
                                                 content=sliced[count] + end,
                                                 footer=footer))
                except discord.errors.Forbidden:
                    await ctx.send(**em(type_="error", content=f"I could not send the message!"))
                if str(reaction) == "<:DM:659338796550193171>":
                    try:
                        await choice.edit(**em("Successfully send the help menu in a private message!"))
                        try: await choice.clear_reactions()
                        except: pass
                    except discord.errors.NotFound:
                        await ctx.send(**em("Successfully send the help menu in a private message!"))
                else:
                    try: await choice.delete()
                    except: pass
        else:
            prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
            cog = self.bot.get_cog(command)
            cmd = self.bot.get_command(command)
            if cog is None and cmd is None:
                await ctx.send(**em("I couldn't find any related command!"))
            else:
                if cog is not None:
                    walker = [c for c in cog.walk_commands()]
                    counter = 0
                    if walker:
                        sub_const, counter = exe_walker(cog)
                        help_const.append(f"{message.join(sub_const)}\n")
                    sliced = formatter.paginate(final.join(help_const))
                    for count in range(len(sliced)):
                        title, end, footer = discord.Embed.Empty, "", False
                        if count == 0:
                            title = f"{cog.qualified_name} command(s) [`{counter}`]:"
                        if count == len(sliced) - 1:
                            end = f"\n*Type {prefix}help command* for more details!"
                            footer = True
                        await ctx.send(**em(title=title, content=sliced[count] + end, footer=footer))
                elif cmd is not None:
                    aliases = ""
                    if cmd.aliases:
                        aliases = f"\nAliases: " + ", ".join(cmd.aliases)
                    if type(cmd) == discord.ext.commands.core.Group:
                        walker = [c for c in cmd.walk_commands()]
                        counter = 0
                        if walker:
                            sub_const, counter = exe_walker(cmd)
                            help_const.append(message.join([r.replace(f"{cmd.qualified_name} ", "") for r in sub_const])
                                              + "\n")
                        sliced = formatter.paginate(final.join(help_const))
                        for count in range(len(sliced)):
                            title, end, pre, footer = discord.Embed.Empty, "", "", False
                            if count == 0:
                                pre = cmd.help + "\n" or ''
                                title = f"{str(cmd.qualified_name).capitalize()} sub-command(s) [`{counter}`]:"
                            if count == len(sliced) - 1:
                                end = f"\n*Type {prefix}help {cmd} sub-command* for more details!"
                                footer = True
                            await ctx.send(**em(title=title, content=pre + sliced[count] + end, footer=footer))
                    elif type(cmd) == discord.ext.commands.core.Command:
                        params = []
                        for item in cmd.clean_params:
                            params.append(item)
                        await ctx.send(**em(title=f"About {cmd.qualified_name}:",
                                            content=f"Usage: {prefix+cmd.qualified_name+ ' '+' '.join(params)}\n"
                                                    f"{cmd.help or ''}{aliases}"))


def setup(bot):
    bot.add_cog(Help(bot))
