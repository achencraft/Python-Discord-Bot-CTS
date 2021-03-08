import os

class Settings:
    def __init__(self):
        self.ADMIN_ROLE=os.getenv('BOT_ADMIN_ROLE','Admin')
        self.GUILD_NAME=os.getenv('GUILD_NAME')
        self.CTS_TOKEN=os.getenv('CTS_TOKEN')
        self.NBR_STOP_PER_PAGE=os.getenv('NBR_STOP_PER_PAGE',20)
        self.BOT_PREFIX=os.getenv('BOT_PREFIX','CTS?')
        self.DISTANCE_MAX=os.getenv('DISTANCE_MAX',5)
        

    def as_string(self):
        ret=""
        for k,v in self.__dict__.items():
            if not k.startswith('_') and k.upper()==k:
                ret+=f"{k}={v}\n"
                
        return ret