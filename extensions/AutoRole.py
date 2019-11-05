import configparser
from discord.ext import commands
from util.core import data, formatter

em = formatter.embed_message

config = configparser.ConfigParser()
config.read("config.cfg")


class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def default(self, ctx):
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        return f"Please use a valid sub-command.\nSee the `{prefix}help {ctx.command.qualified_name}`!"

    @commands.group(name="autorole", aliases=["autor", "auto-r", "auto-role"], invoke_without_command=True)
    async def autorole(self, ctx):
        """Auto-Role group command"""
        await ctx.send(**em(self.default(ctx)))

    @autorole.command(name="add", aliases=["create"])
    async def add(self, ctx, role=None):
        """Add a role to the auto role system.
        The role you provided must be an id"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(**em(type_="error",
                                content="You need to have at least administrator permission to add an auto role!!"))
        else:
            if role is None:
                await ctx.send(**em(type_="error",
                                    content="Please provide a role that I should add to the auto role system!\n"
                                            "For more information you can check out the "
                                            f"__**[docs]({config['DOCS']['customCommands']} \"Alexi Documentation\")**__."))
            else:
                role_id = role
                try:
                    role_id = int(role)
                except ValueError:
                    await ctx.send(**em(type_="error",
                                        content="You should provide a valid role id! *(this is a number)*\n"
                                                "For more information you can check out the "
                                                f"__**[docs]({config['DOCS']['customCommands']} "
                                                f"\"Alexi Documentation\")**__."))
                else:
                    roles = data.get_auto_role(ctx.message.guild.id)
                    role = ctx.message.guild.get_role(role_id=role_id)
                    for _role in roles:
                        if role == _role[0]:
                            await ctx.send(**em(type_="error",
                                                content=f"The autorole for {role.mention} already exists!"))
                    else:
                        if role is None:
                            await ctx.send(**em(type_="error",
                                                content=f"Could not find a role with an id of: {str(role_id)}"))
                        else:
                            data.add_auto_role(ctx.message.guild.id, role.id)
                            await ctx.send(**em(content=f"Successfully created an autorole for the {role.mention} role!"))

    @autorole.command(name="remove", aliases=["delete", "del"])
    async def remove(self, ctx, role=None):
        """Removed a role from the auto role system."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(**em(type_="error",
                                content="You need to have at least administrator permission to remove an autorole!"))
        else:
            if role is None:
                await ctx.send(**em(type_="error",
                                    content="Please provide a role that I should remove from the auto role system!\n"
                                            "For more information you can check out the "
                                            f"__**[docs]({config['DOCS']['customCommands']}"
                                            f"\"Alexi Documentation\")**__."))
            else:
                roles = data.get_auto_role(ctx.message.guild.id)
                if not roles:
                    await ctx.send(**em(type_="error",
                                        content=f"This server doesnt have any auto roles!"))
                else:
                    role_id = role
                    try:
                        role_id = int(role)
                    except ValueError:
                        await ctx.send(**em(type_="error",
                                            content="You should provide a valid role id! *(this is a number)*\n"
                                                    "For more information you can check out the "
                                                    f"__**[docs]({config['DOCS']['customCommands']} "
                                                    f"\"Alexi Documentation\")**__."))
                    else:
                        for _role in roles:
                            if role_id == _role[0]:
                                data.remove_auto_role(ctx.message.guild.id, role_id)
                                await ctx.send(**em(content="I successfully removed the"
                                                            f"autorole for the role with an ID of `{role_id}`!"))
                                return
                        await ctx.send(**em(type_="error",
                                            content="I didn't find an auto role with that ID!"))

    @autorole.command(name="list")
    async def list(self, ctx):
        """Lists all enabled auto roles from the current server"""
        roles = data.get_auto_role(ctx.message.guild.id)
        if not roles:
            await ctx.send(**em(type_="error",
                                content=f"This server doesnt have any auto roles!"))
        else:
            command_list = ", "
            temp_tuple = ()
            final_tuple = ()
            for _role in roles:
                temp_tuple += _role
            for item in temp_tuple:
                _role = ctx.guild.get_role(role_id=item)
                final_tuple += (_role.mention + "(`" + str(item) + "`)",)
            _role_list = command_list.join(final_tuple)
            await ctx.send(**em(content="These are all the auto-roles that apply to this server!\n"
                                        f"Auto roles: {_role_list}"))

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_member_join(self, member):
        if member.guild.id == 634141277788831795:
            if member.bot:
                bot_role = member.guild.get_role(role_id=638388474654752768)
                await member.add_roles(bot_role, reason=f"Auto join bot role for {member.name}")
                return
        auto_roles = data.get_auto_role(member.guild.id)
        if auto_roles:
            for role in auto_roles:
                _role = member.guild.get_role(role_id=role[0])
                await member.add_roles(_role, reason=f"Auto join roles for {member.name}")


def setup(bot):
    bot.add_cog(AutoRole(bot))
