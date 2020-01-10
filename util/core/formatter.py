import discord
import configparser
import datetime
import random
from util.embed_types import message_types as types


def embed_message(content=None, title=None, type_=None, footer=True,
                  color=None, footer_icon=None, footer_message=None, image=None, extra=None, author=None):
    embed_title, embed_content, embed_icon, embed_color = types.get(type_)
    emb_content = embed_content.format(emb_content=content, e=extra)
    title = title or embed_title
    color = color or embed_color or discord.Color(int(hex(random.randint(0, 16581375)), 0))
    embed = discord.Embed(title=title, color=color or discord.Color(random.randint(0, 16581375)),
                          description=emb_content)
    if image is not None:
        embed.set_image(url=image)
    if author is not None:
        embed.set_author(name=author[0], url=author[1], icon_url=author[2])
    if footer:
        if footer_message is None:
            config = configparser.ConfigParser()
            config.read("config.cfg")
            footer_message = (config["UTILITY"]["default_footer_message"])[1:] + ' ' + str(datetime.datetime.now().year)
        embed.set_footer(text=footer_message,
                         icon_url=footer_icon or
                         "https://cdn.discordapp.com/app-icons/634141001769943090/6720b5715d3741482e7a3552fe7106ec.png?"
                         "size=1024")
    return {"embed": embed}


def convert_time(time):
    return time.strftime("%d/%m/%Y | %H:%M:%S")


def paginate(content, limit=1900):
    result = [""]
    lines = content.splitlines(keepends=True)
    i = 0
    for line in lines:
        if len(result[i]) + len(line) <= limit:
            result[i] += line
        else:
            i += 1
            result.append(line)
    return result
