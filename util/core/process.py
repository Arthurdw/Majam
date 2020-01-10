import string
import random
import json
import discord
from util import operators
from util.core import formatter, data

em = formatter.embed_message


async def processed_embed(ctx, output):
    if (str(output).strip())[:1] == "{" and (str(output).strip())[-1:] == "}":
        contents = json.loads(parsing(ctx, output))
        embed = discord.Embed.from_dict(contents)
        await ctx.send(embed=embed)
    else:
        await ctx.send(**em(parsing(ctx, output)))


def generate_string(size=10, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase + '_' + '-'):
    return ''.join(random.choice(chars) for _ in range(size))


def average(amounts):
    total = len(amounts)
    added = 0
    for amount in amounts:
        added += amount
    return added/total


def parsing(ctx, message):
    for operator in operators.get_operators(ctx):
        message = message.replace("{" + str(operator[0]) + "}", str(operator[1]))
    return message


def parsed(ctx):
    for item in data.commands(ctx.guild.id):
        command = str(ctx.invoked_with).lower().strip()
        if command in item:
            parsed_data = data.get_response(ctx.guild.id, command)
            parsed_data = parsing(ctx, parsed_data)
            return parsed_data


def exe_walker(walk):
    _walker = [c for c in walk.walk_commands()]
    checked, sub_const, count = [], [], 0
    if _walker:
        for item in _walker:
            if item.qualified_name not in checked:
                sub_const.append(item.qualified_name)
                checked.append(item.qualified_name)
                count += 1
        return sub_const, count
