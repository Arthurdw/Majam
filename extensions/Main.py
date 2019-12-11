import datetime
import configparser
import json
import glob
import discord
import sqlite3
import ast
import time
import random
from discord.ext import commands
from util.core import data, formatter, checks, GitHub, process

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

    @commands.command(name="trump")
    async def trump(self, ctx):
        images = ["https://cdn.discordapp.com/attachments/357495308768247809/651522787692904468/trumpLoL.png",
                  "https://i.gyazo.com/461e82b5baef8027eb078cb615701dbe.png",
                  "https://i.gyazo.com/thumb/1200/7a99617b42477843537d37877cc17714-png.jpg",
                  "https://i.gyazo.com/thumb/1200/02a49305d33760440a21ec9bd430771a-png.jpg",
                  "https://i.gyazo.com/thumb/1200/7c2a66fd07b10a7c55f9017b2175efc9-png.jpg",
                  "https://i.gyazo.com/thumb/1200/94197dca4a0836dada12fdb5b3573ed7-png.jpg",
                  "https://i.gyazo.com/thumb/1200/05f6e5300e007defbd4f8d8aa135b696-png.jpg",
                  "https://i.gyazo.com/thumb/1200/3978b3f98926d1a73dd02dee31f6f07a-png.jpg",
                  "https://i.gyazo.com/95beb219d043f686128c18a46691d956.png",
                  "https://i.gyazo.com/thumb/1200/8bd8fbb7904c223d28ea30335560509d-png.jpg",
                  "https://i.gyazo.com/4e4b807174df66cdc74a31bbb75cbb84.png"]
        await ctx.send(**em("Trump be like:",
                            image=random.choice(images)))

    @commands.cooldown(1, 3600, commands.BucketType.user)
    @commands.command(name="suggest")
    async def suggest(self, ctx, *, suggestion=None):
        """Suggest a command for the bot!"""
        if suggestion is None:
            await ctx.send(**em(type_="error",
                                content="You need to provide a suggestion!"))
            ctx.command.reset_cooldown(ctx)
            return
        sg_channel = self.bot.get_channel(648249834330914856)
        _suggestion = await sg_channel.send(**em(content=f"**Author**: {ctx.author.mention} *({ctx.author.id})*\n"
                                                         f"**Suggestion**:\n```"
                                                         f"{str(suggestion).lower().capitalize().replace('`', '´')}"
                                                         f"```", footer=False))
        await ctx.send(**em(content=f"Successfully send [your suggestion]({_suggestion.jump_url} \"{ctx.author.name}'s "
                                    f"suggestion!\")!"))
        for item in [648250030943240214, 648250031455076352, 648250031198961685]:
            await _suggestion.add_reaction(self.bot.get_emoji(item))

    @commands.command(name="docs", aliases=["documentation"])
    async def docs(self, ctx):
        """Retrieve the link to the documentation!"""
        await ctx.send(**em(title="Docs:",
                            content=f"Web Docs: [Commands]({config['DOCS']['webDocs']} \"Majam's Website DOCS\")\n"
                                    f"Raw Docs: [MajamRaw]({config['DOCS']['rawDocs']} \"Majam Raw Docs\")"))

    @commands.command(name="invite")
    async def invite(self, ctx):
        """Retrieve a link to invite Majam!"""
        await ctx.send(**em(content="Invite __**[Majam](https://discordapp.com/api/oauth2/authorize?"
                                    "client_id=634141001769943090&permissions=8&scope=bot "
                                    "\"Invite me please :D\")**__"))

    @commands.command(name="support")
    async def support(self, ctx):
        """Retrieve a link to the Majam support server!"""
        await ctx.send(**em(content="Join our __**[Support Server](https://discord.gg/JA6dqWV "
                                    "\"Join Majam's support server!\")**__!"))

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
        try:
            async def send_message(_content):
                try:
                    await process.processed_embed(ctx, _content)
                except json.decoder.JSONDecodeError:
                    await ctx.send(**em(process.parsing(ctx, content)))
            if content is None:
                await ctx.send(**em(type_="error",
                                    content="You need to provide something that I can embed!\nWant to build complex "
                                            "embeds?\nPlease use [Discord JSON formatting](https://embedbuilder.nadeko"
                                            "bot.me/ \"Discord JSON formatter!\") then!",
                                    title="Missing parameter!"))
            else:
                if ctx.author.guild_permissions.administrator:
                    await send_message(content)
                else:
                    content = str(content).replace('@everyone', 'everyone').replace('@here', 'here')
                    await send_message(content)
        except discord.errors.HTTPException:
            if ctx.author.guild_permissions.administrator:
                await ctx.send(**em(content=content))
            else:
                content = str(content).replace('@everyone', 'everyone').replace('@here', 'here')
                await ctx.send(**em(content=content))

    def insert_returns(self, body):
        # insert return stmt if the last expression is a expression statement
        if isinstance(body[-1], ast.Expr):
            body[-1] = ast.Return(body[-1].value)
            ast.fix_missing_locations(body[-1])

        # for if statements, we insert returns into the body and the or else
        if isinstance(body[-1], ast.If):
            self.insert_returns(body[-1].body)
            self.insert_returns(body[-1].orelse)

        # for with blocks, again we insert returns into the body
        if isinstance(body[-1], ast.With):
            self.insert_returns(body[-1].body)

    @checks.management()
    @commands.command(name="eval")
    async def eval_fn(self, ctx, *, cmd):
        """Evaluates input.
        Input is interpreted as newline separated statements.
        If the last statement is an expression, that is the return value.
        Usable globals:
          - `bot`: the bot instance
          - `discord`: the discord module
          - `commands`: the discord.ext.commands module
          - `ctx`: the invocation context
          - `__import__`: the builtin `__import__` function
        Such that `>eval 1 + 1` gives `2` as the result.
        The following invocation will cause the bot to send the text '9'
        to the channel of invocation and return '3' as the result of evaluating
        >eval ```
        a = 1 + 2
        b = a * 2
        await ctx.send(a + b)
        a
        ```
        """
        try:
            first = time.perf_counter()
            fn_name = "_eval_expr"

            cmd = cmd.strip("` ")

            # add a layer of indentation
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            self.insert_returns(body)

            env = {
                'bot': ctx.bot,
                'discord': discord,
                'commands': commands,
                'ctx': ctx,
                '__import__': __import__
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = (await eval(f"{fn_name}()", env))
            last = time.perf_counter()
            await ctx.send(**em(title="Eval:",
                                content=f"**Input:**\n```{cmd}```\n**Output:**```{result}```\nTook "
                                        f"`{round((last-first)*1000, 2)}ms`!"))
        except Exception as e:
            await ctx.send(**em(type_="error",
                                content=e))

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
        """Prefix related commands"""
        prefix = data.get_prefix(bot=self.bot, message=ctx.message, db_only=True)
        await ctx.send(**em(self.default(ctx) + f"\nCurrent prefix: `{prefix}` or just mention me!"))

    @prefix.command(name="reset")
    async def reset(self, ctx):
        """Resets a server their prefix."""
        if not ctx.author.guild_permissions.administrator:
            if ctx.author.id == 232182858251239424:
                pass
            else:
                await ctx.send(**em(type_="error",
                                    content="You need to have at least administrator permission to "
                                            "edit a custom command!"))
                return
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
            if ctx.author.id == 232182858251239424:
                pass
            else:
                await ctx.send(**em(type_="error",
                                    content="You need to have at least administrator permission to "
                                            "edit a custom command!"))
                return
        if prefix is None:
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
        elif process.parsed(ctx) is not None:
            pass
        else:
            if not ctx.author.bot:
                for item in mentions:
                    if item == str(message.content):
                        prefix = data.get_prefix(bot=self.bot, message=message, db_only=True)
                        await ctx.send(**em(f"\nCurrent prefix: `{prefix}` or just mention me!"))
                        break


def setup(bot):
    bot.add_cog(Main(bot))
