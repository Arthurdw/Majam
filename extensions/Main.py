import datetime
import configparser
import json
import glob
import discord
import sqlite3
from discord.ext import commands
from util.core import data, formatter, checks, GitHub

config = configparser.ConfigParser()
config.read("config.cfg")
em = formatter.embed_message
version = GitHub.version()


class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def default(self, ctx):
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        return f"Please use a valid sub-command.\nSee the `{prefix}help {ctx.command.qualified_name}`!"

    @commands.command(name="docs", aliases=["documentation"])
    async def docs(self, ctx):
        """Retrieve the link to the documentation!"""
        await ctx.send(**em(title="Docs:",
                            content=f"Web Docs: [Commands]({config['DOCS']['webDocs']} \"Alexi's Website DOCS\")\n"
                                    f"Raw Docs: [AlexiRaw]({config['DOCS']['rawDocs']} \"Alexi Raw Docs\")"))

    @commands.command(name="invite")
    async def invite(self, ctx):
        """Retrieve a link to invite Alexi!"""
        await ctx.send(**em(content="Invite __**[Alexi](https://discordapp.com/api/oauth2/authorize?"
                                    "client_id=634141001769943090&permissions=8&scope=bot "
                                    "\"Invite me please :D\")**__"))

    @commands.group(name="dev", invoke_without_command=True)
    async def development(self, ctx):
        """All bot dev commands!"""
        await ctx.send(**em(self.default(ctx)))

    @development.command(name='version')
    async def version(self, ctx):
        """Retrieve the latest bot version. (and the current one)"""
        latest = GitHub.version()
        if version == latest:
            embed = formatter.embed_message(content=f"Currently running on version: \n`{version}`",
                                            footer=False)["embed"]
            embed.set_footer(
                text=(config["UTILITY"]["default_footer_message"])[1:-8],
                icon_url="https://cdn.discordapp.com/avatars/634141001769943090/bb49774a1684d9cd1f1958039a25b89c.webp")
            embed.timestamp = datetime.datetime.now()
            await ctx.send(embed=embed)
        else:
            embed = formatter.embed_message(content=f"Currently running on old version: `{version}`\n"
                                                    f"Latest version: `{latest}`",
                                            footer=False)["embed"]
            embed.set_footer(
                text=(config["UTILITY"]["default_footer_message"])[1:-8],
                icon_url="https://cdn.discordapp.com/avatars/634141001769943090/bb49774a1684d9cd1f1958039a25b89c.webp")
            embed.timestamp = datetime.datetime.now()
            await ctx.send(embed=embed)

    @checks.management()
    @development.command(name="update")
    async def update(self, ctx):
        """Updates the bot version."""
        global version
        old_version = version
        version = GitHub.version()
        if version == old_version:
            await ctx.send(**em(content=f"Already running on the latest version!"))
        else:
            await ctx.send(**em(content="Successfully updated the version!\n"
                                        f"From `{old_version}` to `{version}`!"))

    @checks.management()
    @development.command(name="fetch")
    async def _fetch(self, ctx, database=None):
        """Fetch all data from a database of choice!"""
        if database is None:
            databases = ", "
            temp_tuple = ()
            final_tuple = ()
            for _database in glob.glob("db/*.db"):
                temp_tuple += _database
            for db in temp_tuple:
                final_tuple += ("`" + db.replace("db\\", "")[:-3] + "`",)
            await ctx.send(**em(content="You forgot your database my friend...\n"
                                        f"Available databases: {databases}"))
        else:
            fetched = data.fetch_all('db/' + database + '.db')
            _type = type(fetched)
            sub_type = None
            for item in fetched:
                sub_type = type(item)
                break
            if len(fetched) > 1900:
                fetched = str(fetched[1900:]) + '...'
            await ctx.send(**em(title="Fetch information:",
                                content=f"Type: `{_type}`\n"
                                        f"SubType: `{sub_type}\n`"
                                        f"Fetch: ```\n{fetched}\n```"))

    @commands.command(name="say")
    async def say(self, ctx, *, content=None):
        """Embeds a message, you can customize these embeds fully using JSON!"""
        async def send_message(_content):
            if (str(_content).strip())[:1] == "{" and (str(_content).strip())[-1:] == "}":
                contents = json.loads(_content)
                embed = discord.Embed.from_dict(contents)
                await ctx.send(embed=embed)
            else:
                await ctx.send(**em(content))
        if content is None:
            await ctx.send(**em(type_="error",
                                content="You need to provide something that I can embed!",
                                title="Missing parameter!"))
        else:
            if ctx.author.guild_permissions.administrator:
                await send_message(content)
            else:
                content = str(content).replace('@everyone', 'everyone').replace('@here', 'here')
                await send_message(content)

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
        """Prefix related commands"""
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        await ctx.send(**em(self.default(ctx) + f"\nCurrent prefix: `{prefix}` or just mention me!"))

    @prefix.command(name="reset")
    async def reset(self, ctx):
        """Resets a server their prefix."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(**em(type_="error",
                                content="You need to have at least administrator permission to edit a custom command!"))
        else:
            try:
                data.reset_prefix(ctx.guild.id)
                await ctx.send(**em(content=f"Successfully reset the server prefix!"))
            except sqlite3.OperationalError:
                await ctx.send(**em(type_="error",
                                    content="I don't think this server has a custom prefix..."))

    @prefix.command(name="set")
    async def set(self, ctx, prefix=None):
        """Add/Set your custom prefix"""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send(**em(type_="error",
                                content="You need to have at least administrator permission to edit a custom command!"))
        elif prefix is None:
            await ctx.send(**em(self.default(ctx)))
            return
        elif len(prefix) > 1:
            await ctx.send(**em(type_="error",
                                content="The prefix shouldn't exceed 1 character!"))
            return
        else:
            try:
                data.set_prefix(ctx.message.guild.id, ctx.message.author.id, prefix)
                await ctx.send(**em(content=f"Successfully set the server prefix to `{prefix}`"))
            except Exception as e:
                print(e)
                await ctx.send(**em(type_="error",
                                    content="Oh an error occurred, this shouldn't happen please contact the "
                                            "core developer `Arthur#0002`!\n"
                                            f"Exception type: `{type(e).__name__}`\n"
                                            f"Arguments: \n```\n{e.args}\n```"))

    @commands.Cog.listener()
    async def on_message(self, message):
        mentions = ['<@634141001769943090>', '<@!634141001769943090>']
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            pass
        else:
            for item in mentions:
                if item in str(message.content):
                    prefix = data.get_prefix(bot=self.bot, message=message, db_only=True)
                    await ctx.send(**em(f"\nCurrent prefix:`{prefix}` or just mention me!"))
                    break


def setup(bot):
    bot.add_cog(Main(bot))
