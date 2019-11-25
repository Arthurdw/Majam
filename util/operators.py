from util.core import formatter


def get_operators(ctx):
    return [("author", f"{ctx.author.name}#{ctx.author.discriminator}"),
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
             f"{ctx.author.avatar_url}"),
            ("author.default_avatar",
            f"https://cdn.discordapp.com/embed/avatars/{str(int(ctx.author.discriminator) % 5)}.png"),
            ("author.avatar_animated", ctx.author.is_avatar_animated()),
            ("author.mention", ctx.author.mention),
            ("author.int_color", ctx.author.color.value)]
