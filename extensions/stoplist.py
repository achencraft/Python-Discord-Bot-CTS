import discord
from discord.ext import commands
import requests
import structlog
import json
import textdistance
from datetime import datetime

class StopListCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    REACTIONS_NAV = ['⏪', '◀','#⃣','▶','⏩']

    @commands.Cog.listener()
    async def on_ready(self):
        utils_cog = self.bot.get_cog('UtilsCog')
        for guild in self.bot.guilds:
            if guild.name.startswith(utils_cog.settings.GUILD_NAME):
                self.guild = guild

        self.session = requests.Session()
        self.session.auth = (utils_cog.settings.CTS_TOKEN, "")
        self.get_stops_list()



    @commands.command(name='stoplist', aliases=['stations'])
    async def stoplist(self, ctx):
        """
        Commande: CTS? stoplist
        Argument: /
        
        Affiche la liste des stations
        """
        utils_cog = self.bot.get_cog('UtilsCog')
        nbr_stop_per_page = int(utils_cog.settings.NBR_STOP_PER_PAGE)
        nbr_page = len(self.stopslist)//nbr_stop_per_page
        if(len(self.stopslist)%nbr_stop_per_page > 0):
            nbr_page = nbr_page+1

        titre = f"Liste des points d'arrêt CTS - page 1/{nbr_page}"
        content = ""
        stop_to_show = [s[0] for  s in self.stopslist[:nbr_stop_per_page]]
        for stop in enumerate(stop_to_show):
            content += '\n {}'.format(stop[1])

        embed = discord.Embed(title=titre, description=content)
        embed.set_footer(text='stoplist_cts:1')

        msg = await ctx.send(embed=embed)
        
        for reaction in self.REACTIONS_NAV:
            await msg.add_reaction(reaction)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        utils_cog = self.bot.get_cog('UtilsCog')
        nbr_stop_per_page = int(utils_cog.settings.NBR_STOP_PER_PAGE)


        if payload.member.bot:
            return

        channel = self.guild.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        emoji = payload.emoji
        user = payload.member

        
        if message.author != self.bot.user:
            #chek whether bot actually posted the reacted message, otherwise ignores
            return
        
        if user == self.bot.user:
            #ignores if it is the bot voting
            return
        

        if (emoji.name not in self.REACTIONS_NAV):
            #only vote reactions are accepted
            await message.remove_reaction(emoji,user)
            return
        

        for e in message.embeds:
            #check if it's a reaction to a vote
            if ('stoplist_cts' in e.footer.text):
                title = e.title
                try:
                    page = int(e.footer.text.split(':')[1])
                except:
                    return
                break
        else:
            return
        
        nbr_page = len(self.stopslist)//nbr_stop_per_page
        if(len(self.stopslist)%nbr_stop_per_page > 0):
            nbr_page = nbr_page+1

        
        page_to_show = -1

        if(emoji.name == '⏪'):
            if(page != 1):
                page_to_show = 1
        elif(emoji.name == '◀'):
            if(page != 1):
                page_to_show = page-1
        if(emoji.name == '▶'):
            if(page != nbr_page):
                page_to_show = page+1
        if(emoji.name == '⏩'):
            if(page != nbr_page):
                page_to_show = nbr_page
        
        await message.remove_reaction(emoji,user)

        if(page_to_show != -1):
            debut = (page_to_show - 1)*nbr_stop_per_page
            fin = debut + nbr_stop_per_page
            titre = f"Liste des points d'arrêt CTS - page {page_to_show}/{nbr_page}"
            content = ""
            stop_to_show = [s[0] for  s in self.stopslist[debut:fin]]
            for stop in enumerate(stop_to_show):
                content += '\n {}'.format(stop[1])

            embed = discord.Embed(title=titre, description=content)
            embed.set_footer(text=f'stoplist_cts:{page_to_show}')
            await message.edit(embed=embed)

        

    def get_stops_list(self):
        log = structlog.get_logger()
        stopList = []
        codeList = []

        query = self.session.get("https://api.cts-strasbourg.eu/v1/siri/2.0/stoppoints-discovery")
        ans = json.loads(query.text)
        nbr_arret = len(ans["StopPointsDelivery"]["AnnotatedStopPointRef"])
        
        for i in range (0,nbr_arret):
            stopname = ans["StopPointsDelivery"]["AnnotatedStopPointRef"][i]["StopName"]
            stopcode = ans["StopPointsDelivery"]["AnnotatedStopPointRef"][i]["Extension"]["LogicalStopCode"]

            if(stopcode not in codeList):
                codeList.append(stopcode)
                stopList.append((stopname, stopcode))
        log.info('stoplist strasbourg created')
        self.stopslist = sorted(stopList, key=lambda stop: stop[0]) #tri alphabetique

     
def setup(bot):
    bot.add_cog(StopListCog(bot))
