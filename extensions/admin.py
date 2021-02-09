import discord
from discord.ext import commands

from . import perms
class AdminCog(commands.Cog):
    """
    Admin
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.check(perms.is_admin_user)
    @commands.command(name='admin')
    async def admin(self, ctx):
        """
        Commande: CTS? admin
        Argument: /
        
        Ajoute une réaction en te faisant comprendre si t'es admin ou pas :)
        """
        utils_cog = ctx.bot.get_cog('UtilsCog')

        author = ctx.message.author
        role_names = [r.name for  r in author.roles]

        if utils_cog.settings.ADMIN_ROLE in role_names:
            await ctx.message.add_reaction('\U0001F9BE')
        else:
            await ctx.message.add_reaction('\U0001F44E')

def setup(bot):
    bot.add_cog(AdminCog(bot))