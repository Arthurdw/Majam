from util.core import formatter, data


def average(amounts):
    total = len(amounts)
    added = 0
    for amount in amounts:
        added += amount
    return added/total


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
