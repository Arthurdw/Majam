import discord
import configparser
import datetime
import random
from util.embed_types import message_types as types


def embed_message(content=None, title=None, type_=None, footer=True,
                  color=None, footer_icon=None, footer_message=None, image=None):
    embed_title, embed_content, embed_icon, embed_color = types.get(type_)
    title = title or embed_title
    color = color or embed_color
    embed = discord.Embed(title=title, color=color or discord.Color(random.randint(0, 16581375)),
                          description=embed_content.format(emb_content=content))
    if image is not None:
        embed.set_image(url=image)
    if footer:
        if footer_message is None:
            config = configparser.ConfigParser()
            config.read("config.cfg")
            footer_message = (config["UTILITY"]["default_footer_message"])[1:] + datetime.datetime.now().strftime("%Y")
        embed.set_footer(text=footer_message,
                         icon_url=footer_icon or
                         "https://cdn.discordapp.com/avatars/634141001769943090/bb49774a1684d9cd1f1958039a25b89c.webp")
    return {"embed": embed}


def convert_time(time):
    return time.strftime("%d/%m/%Y | %H:%M:%S")
