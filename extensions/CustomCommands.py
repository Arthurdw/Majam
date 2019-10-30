import configparser
from discord import utils
from discord.ext import commands
from util.core import data, formatter

config = configparser.ConfigParser()
config.read("config.cfg")
em = formatter.embed_message

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def default(self, ctx):
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        return f"Please use a valid sub-command.\nSee the `{prefix}help {ctx.command.qualified_name}`!"

    @staticmethod
    def parsed(ctx):
        for item in data.commands(ctx.guild.id):
            command = str(ctx.invoked_with).lower().strip()
            if command in item:
                parsed_data = data.get_response(ctx.guild.id, command)
                return parsed_data

    @commands.guild_only()
    @commands.group(name="command", aliases=["cmd"], invoke_without_command=True)
    async def command(self, ctx):
        """Commands group command!"""
        await ctx.send(**em(self.default(ctx)))

    @commands.guild_only()
    @command.command(name="info", aliases=["about"])
    async def info(self, ctx, command=None):
        """Retrieves information about a command!
        (Creation date, server, creator, name, raw response, response)"""
        pass

    @commands.guild_only()
    @command.command(name='list')
    async def list(self, ctx):
        """Retrieves all the available server commands!"""
        _commands = data.commands(ctx.guild.id)
        if not _commands:
            await ctx.send(**em(content="This server doesn't have any custom commands right now!\n"
                                        f"Create some using `{utils.escape_mentions(ctx.prefix)}command add`"))
        else:
            command_list = ", "
            temp_tuple = ()
            final_tuple = ()
            for command in _commands:
                temp_tuple += command
            for item in temp_tuple:
                final_tuple += ("`" + item + "`",)
            _command_list = command_list.join(final_tuple)
            await ctx.send(**em(content="These are all the server commands!\n"
                                        "You can get more information for each command using"
                                        f"`{utils.escape_mentions(ctx.prefix)}command info`\nCommands: {_command_list}"))

    @commands.guild_only()
    @command.command(name="edit", aliases=["change"])
    async def edit(self, ctx, *, command=None):
        """Edits a command!
        This can not be undone!

        PRO TIP: to make small changes use the 'commands info' command to get the raw data!"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(**em(type_="error",
                                content="You need to have at least administrator permission to edit a custom command!"))
        elif command is None:
            await ctx.send(**em(type_="error",
                                content="Please provide a command that I should remove!\n"
                                        "For more information you can check out the "
                                        f"[__**docs**__]({config['DOCS']['customCommands']} \"Alexi Documentation\")."))
        elif 'return' not in str(command).lower().split(' '):
            await ctx.send(**em(type_="error",
                                content="Please use the correct *syntax* to remove a command.\n"
                                        "For more information you can check out the "
                                        f"[__**docs**__]({config['DOCS']['customCommands']} \"Alexi Documentation\")."))
        else:
            items = str(command).lower().split(" ")
            if 'to' in items:
                try:
                    name, after_to = str(command).lower().split("to")
                    name, after_to = str(name).strip(), str(after_to).strip()
                    new_name, response = after_to.split('return')
                    new_name, response = str(new_name).strip(), str(response).strip()
                except ValueError:
                    _name = str(command).lower().split("to")
                    name = _name[0].strip()
                    _after_to = command[len(_name[0] + 'to'):]
                    after_to = str(_after_to).strip()
                    sliced = after_to.split('return')
                    new_name = sliced[0].strip()
                    response = after_to[len(sliced[0] + 'return'):]
                data.edit_command(ctx.guild.id, name, new_name, response)
                await ctx.send(**em(content=f"Successfully updated the `{name}` command!\n"
                                            f"Changed the name from `{name}` to `{new_name}`!\n"
                                            f"The new output will be this:\n```\n{response}\n```"))
            else:
                try:
                    name, response = str(command).lower().split("return")
                    name, response = str(name).strip(), str(response).strip()
                except ValueError:
                    _name = str(command).lower().split("return")
                    name = _name[0].strip()
                    _response = command[len(_name[0] + 'return'):]
                    response = _response.strip()
                data.edit_command(ctx.guild.id, name, name, response)
                await ctx.send(**em(content=f"Successfully updated the `{name}` command!\n"
                                            f"The new output will be this:\n```\n{response}\n```"))

    @commands.guild_only()
    @command.command(name="remove", aliases=["delete", "del"])
    async def remove(self, ctx, *, command=None):
        """Permanently removes a command!
        This can not be undone!"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(**em(type_="error",
                                content="You need to have at least administrator permission to remove a custom "
                                        "command!"))
        elif command is None:
            await ctx.send(**em(type_="error",
                                content="Please provide a command that I should remove!\n"
                                        "For more information you can check out the "
                                        f"[__**docs**__]({config['DOCS']['customCommands']} \"Alexi Documentation\")."))
        else:
            name = str(command).lower().strip()
            if data.get_command(ctx.message.guild.id, name) is None or \
                    data.get_command(ctx.message.guild.id, name) == []:
                await ctx.send(**em(type_="error",
                                    content=f"This command doesnt exist. (`{name}`)\n"
                                            "Please give right the command name!"))
            else:
                data.remove_command(ctx.guild.id, name)
                await ctx.send(**em(content=f"Successfully removed the command: `{name}`.\n"
                                            f"This was requested by: {ctx.author.mention}"))

    @commands.guild_only()
    @command.command(name="add", aliases=["create"])
    async def add(self, ctx, *, command=None):
        """Add a custom command!
        ⇒ !command add foo return bar
        ⇒ !foo
        ⇐ bar"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(**em(type_="error",
                                content="You need to have at least administrator permission to add a custom command!"))
        elif command is None:
            await ctx.send(**em(type_="error",
                                content="Please provide a command *name* and a *response*!\n"
                                        "For more information you can check out the "
                                        f"[__**docs**__]({config['DOCS']['customCommands']} \"Alexi Documentation\")."))
        elif 'return' not in str(command).lower().split(' '):
            await ctx.send(**em(type_="error",
                                content="Please use the correct *syntax* to add a command.\n"
                                        "For more information you can check out the "
                                        f"[__**docs**__]({config['DOCS']['customCommands']} \"Alexi Documentation\")."))
        else:
            try:
                name, response = str(command).lower().split("return")
                name, response = str(name).strip(), str(response).strip()
            except ValueError:
                _name = str(command).lower().split("return")
                name = _name[0].strip()
                _response = command[len(_name[0] + 'return'):]
                response = _response.strip()
            if response == "":
                await ctx.send(**em(type_="error",
                                    content="You need to give me a response!"))
            elif data.get_command(ctx.message.guild.id, name) is None or\
                    data.get_command(ctx.message.guild.id, name) == []:
                if len(str(name).strip()) > 10:
                    char = 'characters'
                    if len(str(name).strip())-10 == 1:
                        char = 'character'
                    await ctx.send(**em(type_="error",
                                        content="You can't create a command name that is more than `10` characters!\n"
                                                f"`{name}` is `{len(str(name).strip())}` characters!\n"
                                                f"That's `{len(str(name).strip())-10}` {char} to much!"))
                else:
                    data.add_command(ctx.message.guild.id, ctx.message.author.id, name, response)
                    await ctx.send(**em(content="Successfully created a command with the following specifications:\n"
                                                f"Name: `{name}`\n"
                                                f"Response: `{response}`"))
            else:
                await ctx.send(**em(type_="error",
                                    content=f"This command already exists. (`{name}`)\n"
                                            "Command Response:\n"
                                            f"```\n{data.get_response(ctx.message.guild.id, name)}\n```\n"
                                            "Please give the command another name!"))

    @commands.guild_only()
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(**em(CustomCommands.parsed(ctx)))


def setup(bot):
    bot.add_cog(CustomCommands(bot))
