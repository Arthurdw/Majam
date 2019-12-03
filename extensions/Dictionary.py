import discord
from discord.ext import commands
from pythonary import Oxford, errors
from util.core import formatter

em = formatter.embed_message
app = Oxford.Dictionary(app_id="55afa013",
                        app_key="b596812274d2c34d4a353a3e4226af26")


class Dictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="define", aliases=["dict", "def"])
    async def define(self, ctx, content=None):
        if content is None:
            await ctx.send(**em(content="Your request had no content, can't return anything!"))
            ctx.command.reset_cooldown(ctx)
            return
        try:
            app.Select(word=str(content).strip().lower())
            sep = "\n\n"
            full_def = [f"{app.definition().capitalize()}",
                        f"**Short definition:**\n{app.short_definition().capitalize()}",
                        f"**Example:**\n{app.example().capitalize()}",
                        f"**Etymologies(s):**\n{app.etymologies().capitalize()}",
                        f"**Phonetic:** *({app.phonetic_notation()})*\n`{app.phonetic()}`",
                        f"** ---- Sub-Definition ---- **\n{app.sub_definition().capitalize()}",
                        f"**Short definition:**\n{app.sub_short_definition().capitalize()}",
                        f"**Example:**\n{app.sub_example().capitalize()}",
                        f"**[AudioFile]({app.audiofile()} \"Audio file spoken in {app.audiofile_dialect()}\")**",
                        "*Provided by [Oxford dictionary](https://en.wikipedia.org/wiki/Oxford_English_Dictionary "
                        "\"Oxford dictionary\")!\n(using [Pythonary](https://pypi.org/project/pythonary/ "
                        "\"Pythonary PyPi\"))*"]
            await ctx.send(**em(title=f"Definition: {app.name().capitalize()}",
                                content=sep.join(full_def)))
        except errors.NotFound:
            await ctx.send(**em(type_="error", content="Couldn't find that word.\nTry putting it in a singular form!"))
        except errors.UNKError:
            await ctx.send(**em(type_="error", content="Oh, an unknown exception occurred!"))
        except errors.ApplicationError:
            await ctx.send(**em(type_="error", content="Oh, I can't fetch no more words until next month!"))
        except errors.BadRequest:
            await ctx.send(**em(type_="error", content="Something went wrong! *(404)*\nThis is an internal error!"))
        except errors.RequestToLong:
            await ctx.send(**em(type_="error",
                                content="Word is too long!\nPlease  keep your word under `128` characters!"))
        except errors.InternalError:
            await ctx.send(**em(type_="error",
                                content="Oh, well this isn't supposed to happen.\nAn internal API error occurred!"))
        except errors.BadGateway:
            await ctx.send(**em(type_="error", content="The place we get our definitions from is down. :("))
        except errors.ServiceUnavailable:
            await ctx.send(**em(type_="error",
                                content="The place we get our definitions from is overloaded. :("))
        except errors.GatewayTimeout:
            await ctx.send(**em(type_="error",
                                content="Oh, seems like Oxford doesn't have time for us...\n*(Internal failure, please "
                                        "try again later!)*"))
        except KeyError:
            sep = "\n\n"
            try: short_def = f"**Short definition:**\n{app.short_definition().capitalize()}"
            except: short_def = ""
            try: example = f"**Example:**\n{app.example().capitalize()}",
            except: example = ""
            try: etymologies = f"**Etymologies(s):**\n{app.etymologies().capitalize()}"
            except: etymologies = ""
            try: phonetic = f"**Phonetic:** *({app.phonetic_notation()})*\n`{app.phonetic()}`"
            except: phonetic = ""
            try: sub_def = f"** ---- Sub-Definition ---- **\n{app.sub_definition().capitalize()}"
            except: sub_def = ""
            try: sub_short_def = f"**Short definition:**\n{app.sub_short_definition().capitalize()}"
            except: sub_short_def = ""
            try: sub_short_example = f"**Example:**\n{app.sub_example().capitalize()}"
            except: sub_short_example = ""
            try: audio_file = f"**[AudioFile]({app.audiofile()} \"Audio file spoken in {app.audiofile_dialect()}\")**"
            except: audio_file = ""
            full_def = [f"{app.definition().capitalize()}", short_def, example, etymologies, phonetic, sub_def,
                        sub_short_def, sub_short_example, audio_file,
                        "*Provided by [Oxford dictionary](https://en.wikipedia.org/wiki/Oxford_English_Dictionary "
                        "\"Oxford dictionary\")!\n(using [Pythonary](https://pypi.org/project/pythonary/ "
                        "\"Pythonary PyPi\"))*"]
            await ctx.send(**em(title=f"Definition: {app.name().capitalize()}",
                                content=sep.join(full_def)))


def setup(bot):
    bot.add_cog(Dictionary(bot))
