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


    @commands.Cog.listener()
    async def on_ready(self):
        utils_cog = self.bot.get_cog('UtilsCog')
        for guild in self.bot.guilds:
            if guild.name.startswith(utils_cog.settings.GUILD_NAME):
                self.guild = guild

        self.session = requests.Session()
        self.session.auth = (utils_cog.settings.CTS_TOKEN, "")



    @commands.command(name='next', aliases=['prochain','passage'])
    async def next(self, ctx, *args):
        """
        Commande: CTS? next <nom de station ou code>
        Argument: nom de la station en toutes lettres
        
        Affiche les prochains passages en station
        """
        station = " ".join(args)
        utils_cog = self.bot.get_cog('UtilsCog')
        distance = 0
        content = "Aucun passage"
        station_name = station


        if station.strip('-').isnumeric():
            if self.stopIdExists(station):
                stop_id = int(station)
            else:
                distance = int(utils_cog.settings.DISTANCE_MAX) + 1
        else:
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



    def get_next_vehicle(self, stop_id):
        passages=[]
        stop_name = ""

        query = self.session.get(f"https://api.cts-strasbourg.eu/v1/siri/2.0/stop-monitoring?MaximumStopVisits=3&MinimumStopVisitsPerLine=1&MonitoringRef={stop_id}")
        ans = json.loads(query.text)     

        if len(ans["ServiceDelivery"]["StopMonitoringDelivery"][0]['MonitoredStopVisit']) > 0:
            stop_name = ans["ServiceDelivery"]["StopMonitoringDelivery"][0]['MonitoredStopVisit'][0]['MonitoredVehicleJourney']['MonitoredCall']['StopPointName']
            
            for passage in ans["ServiceDelivery"]["StopMonitoringDelivery"][0]['MonitoredStopVisit']:
                line = passage['MonitoredVehicleJourney']['PublishedLineName']
                destination = passage['MonitoredVehicleJourney']['DestinationName']
                heure_passage = passage['MonitoredVehicleJourney']['MonitoredCall']['ExpectedDepartureTime']
                temps = arrow.get(heure_passage)
                utcnow = utc = arrow.utcnow()
                now = utc.to('Europe/Paris')
                diff = temps - now
                temps_attente = str(diff.seconds//60)

                out = (line,destination,temps_attente)
                passages.append(out)
        
        print(passages)

        return (stop_name,passages)





    def findClosestStopName(self, input):
    
        stoplistCog = self.bot.get_cog('StopListCog')
        stoplist = stoplistCog.stopslist

        input = input.lower().replace(" ","_")
        
        scores =  [ textdistance.levenshtein(input, x[0].lower().replace(" ","_")) for x in stoplist ]
        best_name = stoplist[scores.index(min(scores))]

        return [best_name,min(scores)]

    def stopIdExists(self, stop_id):        
        stoplistCog = self.bot.get_cog('StopListCog')
        stoplist = stoplistCog.stopslist       
        id_list =  [ x[1] for x in stoplist ]
        if(stop_id in id_list):
            return True
        return False


     
def setup(bot):
    bot.add_cog(NextCog(bot))
