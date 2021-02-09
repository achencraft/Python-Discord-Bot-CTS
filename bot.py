import os
import discord
import structlog
from dotenv import load_dotenv 
from discord.ext import commands


log = structlog.get_logger()
dotenv_path = join(dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    log.info('loading environment')
    load_dotenv(dotenv_path)

TOKEN = os.getenv('BOT_TOKEN')
BOT_PREFIX = os.getenv('BOT_PREFIX', 'CTS?')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=BOT_PREFIX,  case_insensitive=True, intents=intents)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot_log_message(f"Bot-CTS a démarré en version")


async def bot_log_message(*args, **kwargs):
    BOT_LOG_CHANNEL_ID = 627259758084358144

    try:
        if BOT_LOG_CHANNEL_ID:
            BOT_LOG_CHANNEL_ID = int(BOT_LOG_CHANNEL_ID)
            bot_log_channel = discord.utils.get(bot.get_all_channels(), id=BOT_LOG_CHANNEL_ID)
            
            if bot_log_channel:
                await bot_log_channel.send(*args, **kwargs)
            else:
                log.warning(f'Could not find bot log channel with id {BOT_LOG_CHANNEL_ID}')
    except Exception as e:
        print('Could not post message to bot log channel')

    
if __name__ == "__main__":

    bot.run(TOKEN, bot=True, reconnect=True)
