import discord
from discord.ext import commands
import requests
import structlog
import typing
import json
import textdistance
from datetime import datetime
import arrow

class NextCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    REACTIONS_NAV = ['⏪', '◀','#⃣','▶','⏩']

    @commands.Cog.listener()
    async def on_ready(self):
        utils_cog = self.bot.get_cog('UtilsCog')
        for guild in self.bot.guilds:
            if guild.name.startswith(utils_cog.settings.GUILD_NAME):
                self.guild = guild

        self.lux_token = utils_cog.settings.LUXTRAM_TOKEN
        self.get_stops_list()



    @commands.command(name='lux', aliases=['luxembourg'])
    async def lux(self, ctx, *args):
        """
        Commande: CTS? lux <action> <argument>

        Action: "stations" ou "next"
        Argument: nom de la station en toutes lettres
        
        Affiche les prochains passages en station
        """
 

        if(args[0] == "stations"):
            await self.stoplist(ctx)
        elif(args[0] == "next"):
            await self.next(ctx,args)
            return
        else:
            return
        
    async def next(self,ctx,args):
        print(args)
        station = " ".join(args[1:])
        utils_cog = self.bot.get_cog('UtilsCog')
        distance = 0
        content = "Aucun passage"
        station_name = station

  
        #si la saisie est une chaine
        if not station.strip('-').isnumeric():
            closest_name = self.findClosestStopName(station)
            stop_id = closest_name[0][1]
            distance = closest_name[1]
            station_name = closest_name[0][0]

        if(distance < int(utils_cog.settings.DISTANCE_MAX)):
            passages = self.get_next_vehicle(stop_id)
            if not len(passages[1]) == 0:
                station_name = passages[0]
                content = ""
            titre = f"Prochains passages - {station_name}"        
            for passage in passages[1]:
                content += '\n Ligne {} > {} : **{}** min'.format(passage[0],passage[1],passage[2])
        else:
            titre = "Prochains passages"  
            content = "Je n'ai pas réussi à trouver cette station :/"

        
        embed = discord.Embed(title=titre, description=content)
        msg = await ctx.send(embed=embed)

    def findClosestStopName(self, input):
    
        stoplist = self.stopslist
        input = input.lower().replace(" ","_")        
        scores =  [ textdistance.levenshtein(input, x[0].lower().replace(" ","_")) for x in stoplist ]
        best_name = stoplist[scores.index(min(scores))]
        return [best_name,min(scores)]

    def get_next_vehicle(self, stop_id):
        passages=[]
        stop_name = ""

        query = requests.Session().get("https://cdt.hafas.de/opendata/apiserver/departureBoard?accessId="+self.lux_token+"&lang=fr&id="+stop_id+"&format=json")
        ans = json.loads(query.text)     

        print(len(ans["Departure"]))
        if len(ans["Departure"]) > 0:
            print(ans["Departure"][0]['Notes'])
            stop_name = ans["Departure"][0]['stop']
            print(stop_name)

            for passage in ans["Departure"]:
                line = passage['trainNumber']
                destination = passage['direction']
                heure_passage = passage['date']+" "+passage['time']
                temps = arrow.get(heure_passage,'YYYY-MM-DD HH:mm:ss')
                print(temps)
                utc = arrow.utcnow()
                now = utc.shift(hours=+1)
                print(now)
                diff = temps - now
                print(diff)
                temps_attente = str(diff.seconds//60)

                out = (line,destination,temps_attente)
                passages.append(out)
            
        print(passages)

        return (stop_name,passages)

    async def stoplist(self, ctx):
        """
        Commande: CTS? lux stations
        Argument: /
        
        Affiche la liste des stations au luxembourg
        """
        utils_cog = self.bot.get_cog('UtilsCog')
        nbr_stop_per_page = int(utils_cog.settings.NBR_STOP_PER_PAGE)
        nbr_page = len(self.stopslist)//nbr_stop_per_page
        if(len(self.stopslist)%nbr_stop_per_page > 0):
            nbr_page = nbr_page+1

        titre = f"Liste des points d'arrêt au Luxembourg - page 1/{nbr_page}"
        content = ""
        stop_to_show = [s[0] for  s in self.stopslist[:nbr_stop_per_page]]
        for stop in enumerate(stop_to_show):
            content += '\n {}'.format(stop[1])

        embed = discord.Embed(title=titre, description=content)
        embed.set_footer(text='stoplist_lux:1')

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
            if ('stoplist_lux' in e.footer.text):
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
            titre = f"Liste des points d'arrêt au Luxembourg - page {page_to_show}/{nbr_page}"
            content = ""
            stop_to_show = [s[0] for  s in self.stopslist[debut:fin]]
            for stop in enumerate(stop_to_show):
                content += '\n {}'.format(stop[1])

            embed = discord.Embed(title=titre, description=content)
            embed.set_footer(text=f'stoplist_lux:{page_to_show}')
            await message.edit(embed=embed)


    def get_stops_list(self):
        log = structlog.get_logger()
        stopList = []
        codeList = []

        with requests.Session() as s:
            query = s.get("https://cdt.hafas.de/opendata/apiserver/location.nearbystops?accessId="+self.lux_token+"&originCoordLong=6.09528&originCoordLat=49.77723&maxNo=5000&r=100000&format=json")
        
        ans = json.loads(query.text)
        nbr_arret = len(ans["stopLocationOrCoordLocation"])
        
        for i in range (0,nbr_arret):
            stopname = ans["stopLocationOrCoordLocation"][i]['StopLocation']["name"]
            stopcode = ans["stopLocationOrCoordLocation"][i]['StopLocation']["extId"]

            if(stopcode not in codeList):
                codeList.append(stopcode)
                stopList.append((stopname, stopcode))
        log.info('stoplist created')
        self.stopslist = sorted(stopList, key=lambda stop: stop[0]) #tri alphabetique



     
def setup(bot):
    bot.add_cog(NextCog(bot))
