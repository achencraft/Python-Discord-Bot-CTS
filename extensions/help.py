import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        utils_cog = self.bot.get_cog('UtilsCog')
        for guild in self.bot.guilds:
            if guild.name.startswith(utils_cog.settings.GUILD_NAME):
                self.guild = guild


    @commands.command(name='aide', aliases=[''])
    async def help(self, ctx):
        """
        Commande: !help ou !aide
        Argument: /
        
        Affiche un embed avec des informations pour obtenir de l'aide
        """
        
        utils = self.bot.get_cog('UtilsCog')

        embed = discord.Embed(title="Aide")
        
        embed.description = ""
        embed.description += "==== BOT CTS - Aide ====\n"
        embed.description += "- `CTS? aide` : pour obtenir l'aide des commandes\n"
        embed.description += "- `CTS? stations` : pour obtenir la liste des stations\n"
        embed.description += "- `CTS? next <station>` : pour obtenir les prochains passages en station\n"

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        Affiche l'aide si un erreur de commande survient
        """       
        if(ctx.command == None):
            await self.help(ctx)
            
    @commands.Cog.listener()
    async def on_message(self, ctx):
        """
        Affiche l'aide si l'utilisateur tape le préfix sans commande
        """
        utils_cog = self.bot.get_cog('UtilsCog')
        if(ctx.content == utils_cog.settings.BOT_PREFIX.replace(' ', '')):
            await self.help(ctx.channel)
            

  
def setup(bot):
    bot.add_cog(HelpCog(bot))
