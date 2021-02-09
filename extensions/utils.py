import discord
from discord.ext import commands
import structlog 
import os

from . import settings, perms

import traceback

log = structlog.get_logger()

class UtilsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings = settings.Settings()

    async def bot_log_message(self, *args, **kwargs):
        BOT_LOG_CHANNEL_ID = os.getenv('BOT_LOG_CHANNEL_ID')

        try:
            if BOT_LOG_CHANNEL_ID:
                BOT_LOG_CHANNEL_ID = int(BOT_LOG_CHANNEL_ID)
                bot_log_channel = discord.utils.get(self.bot.get_all_channels(), id=BOT_LOG_CHANNEL_ID)
                
                if bot_log_channel:
                    await bot_log_channel.send(*args, **kwargs)
                else:
                    log.warning(f'Could not find bot log channel with id {BOT_LOG_CHANNEL_ID}')
        except Exception as e:
            log.error('Could not post message to bot log channel', exc_info=e)
            

        
   
    @commands.command(name='show_settings')
    @commands.check(perms.is_admin_user)
    async def show_settings(self, ctx):
        await self.bot_log_message("Settings")
        await self.bot_log_message("-------")
        await self.bot_log_message(self.settings.as_string())


        

def setup(bot):
    bot.add_cog(UtilsCog(bot))