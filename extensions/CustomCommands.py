import configparser
import datetime
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
    def parse_command(command):
        _name = str(command).lower().split("return")
        name = _name[0].strip()
        _response = command[len(_name[0] + 'return'):]
        response = _response.strip()
        return [name, response]

    @staticmethod
    def parsed(ctx):
        operators = [("author", f"{ctx.author.name}#{ctx.author.discriminator}"),
                     ("author.name", ctx.author.name),
                     ("author.discriminator", ctx.author.discriminator),
                     ("author.id", ctx.author.id),
                     ("author.nickname", ctx.author.display_name),
                     ("author.bot", ctx.author.bot),
                     ("author.color", f"#{str(hex(ctx.author.color.r))[-2:]}"
                                      f"{str(hex(ctx.author.color.g))[-2:]}"
                                      f"{str(hex(ctx.author.color.b))[-2:]}"),
                     ("author.created", formatter.convert_time(ctx.author.created_at)),
                     ("author.avatar",
                      f"https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar_url}.webp?size=1024"),
                     ("author.default_avatar",
                      f"https://cdn.discordapp.com/embed/avatars/{str(int(ctx.author.discriminator) % 5)}.png"),
                     ("author.avatar_animated", ctx.author.is_avatar_animated()),
                     ("author.mention", ctx.author.mention)]
        for item in data.commands(ctx.guild.id):
            command = str(ctx.invoked_with).lower().strip()
            if command in item:
                parsed_data = data.get_response(ctx.guild.id, command)
                for operator in operators:
                    parsed_data = parsed_data.replace("{" + str(operator[0]) + "}", str(operator[1]))
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
        if command is None:
            await ctx.send(**em(content="Please provide a command that I should show information about!"))
        cmd_info = data.command_info(ctx.guild.id, command)
        extra = ""
        if len(command) < 11:
            extra = f"\nCreate it using `{utils.escape_mentions(ctx.prefix)}command add " \
                    f"{command} return My amazing command!`"
        if not cmd_info:
            await ctx.send(**em(content=f"This server doesnt have this custom command right now!{extra}"))
        else:
            raw_creation_date = datetime.datetime.strptime(cmd_info[0][0], '%Y-%m-%d %H:%M:%S.%f')
            guild = self.bot.get_guild(cmd_info[0][1])
            await ctx.send(**em(title="Command information:",
                                content=f"Creation Date: `{formatter.convert_time(raw_creation_date)}`\n"
                                        f"Command: `{cmd_info[0][3]}`\n"
                                        f"Author: <@{cmd_info[0][2]}>\n"
                                        f"Guild: `{guild.name}`\n"
                                        f"Raw response: `{str(cmd_info[0][4]).replace('`', '´')}`\n"))

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
                                        f"`{utils.escape_mentions(ctx.prefix)}command info`\n"
                                        f"Commands: {_command_list}"))

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
                                content="Please provide a command that I should edit!\n"
                                        "For more information you can check out the "
                                        f"__**[docs]({config['DOCS']['rawDocs']} \"Alexi Documentation\")**__."))
        elif 'return' not in str(command).lower().split(' '):
            await ctx.send(**em(type_="error",
                                content="Please use the correct *syntax* to edit a command.\n"
                                        "For more information you can check out the "
                                        f"__**[docs]({config['DOCS']['rawDocs']} \"Alexi Documentation\")**__."))
        else:
            cmd_name = str(command).lower().strip()
            if data.command_info(ctx.message.guild.id, cmd_name) is None or \
                    data.command_info(ctx.message.guild.id, cmd_name) == []:
                await ctx.send(**em(type_="error",
                                    content=f"This command doesnt exist. (`{cmd_name}`)\n"
                                            "Please give right the command name!"))
            elif 'to' in cmd_name:
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
                                            f"The new output will be this:\n"
                                            f"```\n{str(response).replace('`', '´')}\n```"))
            else:
                name, response = CustomCommands.parse_command(command)
                data.edit_command(ctx.guild.id, name, name, response)
                await ctx.send(**em(content=f"Successfully updated the `{name}` command!\n"
                                            f"The new output will be this:\n"
                                            f"```\n{str(response).replace('`', '´')}\n```"))

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
                                        f"__**[docs]({config['DOCS']['rawDocs']} \"Alexi Documentation\")**__."))
        else:
            name = str(command).lower().strip()
            if data.command_info(ctx.message.guild.id, name) is None or \
                    data.command_info(ctx.message.guild.id, name) == []:
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
                                        f"__**[docs]({config['DOCS']['rawDocs']} \"Alexi Documentation\")**__."))
        elif 'return' not in str(command).lower().split(' '):
            await ctx.send(**em(type_="error",
                                content="Please use the correct *syntax* to add a command.\n"
                                        "For more information you can check out the "
                                        f"__**[docs]({config['DOCS']['rawDocs']} \"Alexi Documentation\")**__."))
        else:
            name, response = CustomCommands.parse_command(command)
            if response == "":
                await ctx.send(**em(type_="error",
                                    content="You need to give me a response!"))
            elif data.command_info(ctx.message.guild.id, name) is None or\
                    data.command_info(ctx.message.guild.id, name) == []:
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
                                                f"Response: `{str(response).replace('`', '´')}`"))
            else:
                response = data.get_response(ctx.message.guild.id, name).replace('`', '´')
                await ctx.send(**em(type_="error",
                                    content=f"This command already exists. (`{name}`)\n"
                                            "Command Response:\n"
                                            f"```\n{response}\n```\n"
                                            "Please give the command another name!"))

    @commands.guild_only()
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            output = CustomCommands.parsed(ctx)
            if output is not None:
                await ctx.send(**em(output))


def setup(bot):
    bot.add_cog(CustomCommands(bot))
