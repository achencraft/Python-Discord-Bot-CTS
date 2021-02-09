def is_admin_user(ctx):
    utils_cog = ctx.bot.get_cog('UtilsCog')
    author = ctx.author
    role_names = [r.name for  r in author.roles]
    return utils_cog.settings.ADMIN_ROLE in role_names

